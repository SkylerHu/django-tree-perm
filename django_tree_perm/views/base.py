#!/usr/bin/env python
# coding=utf-8
import json
import functools
from http import HTTPStatus

from django.db import models
from django.views import View
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.exceptions import ValidationError
from django.utils.decorators import classonlymethod
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import AbstractUser

from django_tree_perm import exceptions
from django_tree_perm.models.utils import user_to_json


class BaseView(View):

    @classmethod
    def parese_request_body(cls, request):
        """解析提交的数据"""
        if request.content_type == "application/json":
            data = json.loads(request.body)
        elif request.content_type == "multipart/form-data":
            data = dict(request.POST.dict())
        else:
            raise NotImplementedError(f"not support content-type={request.content_type}")
        return data

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except (ValidationError, exceptions.ParamsValidateException) as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)


class BasePermissionView(BaseView):

    def dispatch(self, request, *args, **kwargs):
        try:
            user = request.user
            if not user or not user.is_authenticated:
                raise exceptions.PermDenyException("Not allowed without login.")
            return super().dispatch(request, *args, **kwargs)
        except exceptions.PermDenyException as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.FORBIDDEN)


class BaseModelSerializer(object):

    def __init__(self, instance, many=False, context=None):
        self.instance = instance
        self.many = many
        self.context = context or {}

    def to_representation(self, instance):
        if isinstance(instance, AbstractUser):
            return user_to_json(instance)
        return instance.to_json()

    @property
    def data(self):
        if self.many:
            value = [self.to_representation(obj) for obj in self.instance]
        else:
            value = self.to_representation(self.instance)
        return value


class BaseModelView(BasePermissionView):

    model = None
    serializer_class = BaseModelSerializer

    @classonlymethod
    def as_view(cls, **initkwargs):
        if not cls.model:
            raise NotImplementedError("model cannot be empty.")
        return super().as_view(**initkwargs)


class BaseListModelMixin(BaseModelView):

    search_fields = []
    filter_fields = []
    ordering = ["id"]

    def get_queryset(self, request, **kwargs):
        return self.model.objects.all().order_by(*self.ordering)

    def filter_queryset(self, request, **kwargs):
        queryset = self.get_queryset(request, **kwargs)
        queryset = self.filter_by_fields(request, queryset)
        queryset = self.filter_by_search(request, queryset)
        return queryset

    def filter_by_search(self, request, queryset):
        search = request.GET.get("search", None)
        if search and self.search_fields:
            query = functools.reduce(
                lambda a, b: a | b, [models.Q(**{f"{field}__contains": search}) for field in self.search_fields]
            )
            queryset = queryset.filter(query)
        return queryset

    def filter_by_fields(self, request, queryset):
        for field in self.filter_fields:
            value = request.GET.get(field, None)
            if not value:
                continue
            # bool类型筛选用0/1筛选
            if field.endswith("__in"):
                value = value.split(",")
            queryset = queryset.filter(**{field: value})

        return queryset

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(request, **kwargs)

        count = queryset.count()
        # 分页返回
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        paginator = Paginator(queryset, page_size)

        serializer = self.serializer_class(paginator.get_page(page), many=True, context={"request": request})

        return JsonResponse({"count": count, "results": serializer.data}, status=HTTPStatus.OK)


class BaseCreateModelMixin(BaseModelView):

    def check_create_permission(self, request, **kwargs):
        pass

    def post(self, request, *args, **kwargs):
        data = self.parese_request_body(request)
        self.check_create_permission(request, data=data)
        instance = self.model(**data)
        instance.full_clean()
        instance.save()

        serializer = self.serializer_class(instance, context={"request": request})
        return JsonResponse(serializer.data, status=HTTPStatus.CREATED)


class BaseGenericModelMixin(BaseModelView):

    model = None
    pk_field = None

    def get_object(self, pk):
        if self.pk_field and pk and not pk.isdigit():
            obj = get_object_or_404(self.model, **{self.pk_field: pk})
        else:
            obj = get_object_or_404(self.model, pk=pk)

        return obj

    def check_object_permissions(self, request, obj, **kwargs):
        pass


class BaseRetrieveModelMixin(BaseGenericModelMixin):

    def get(self, request, *args, pk=None, **kwargs):
        instance = self.get_object(pk)
        serializer = self.serializer_class(instance, context={"request": request})
        return JsonResponse(serializer.data, status=HTTPStatus.OK)


class BaseUpdateModelMixin(BaseGenericModelMixin):

    def patch(self, request, *args, pk=None, **kwargs):
        instance = self.get_object(pk)
        data = self.parese_request_body(request)

        self.check_object_permissions(self.request, instance, data=data)

        for k, v in data.items():
            setattr(instance, k, v)
        instance.full_clean()
        instance.save()
        serializer = self.serializer_class(instance, context={"request": request})
        return JsonResponse(serializer.data, status=HTTPStatus.OK)


class BaseDestoryModelMixin(BaseGenericModelMixin):
    def delete(self, request, *args, pk=None, **kwargs):
        instance = self.get_object(pk)

        self.check_object_permissions(self.request, instance)

        serializer = self.serializer_class(instance, context={"request": request})
        data = serializer.data

        instance.delete()
        return JsonResponse(data, status=HTTPStatus.NO_CONTENT)