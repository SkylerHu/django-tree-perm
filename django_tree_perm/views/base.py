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
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
        return data

    def dispatch(self, request, *args, **kwargs):
        try:
            return super().dispatch(request, *args, **kwargs)
        except (ValidationError, exceptions.ParamsValidateException) as e:
            return JsonResponse({"error": str(e)}, status=HTTPStatus.BAD_REQUEST)


class BaseModelView(BaseView):

    model = None

    @classonlymethod
    def as_view(cls, **initkwargs):
        if not cls.model:
            raise NotImplementedError("model cannot be empty.")
        return super().as_view(**initkwargs)

    def model_to_json(self, request, instance):
        if isinstance(instance, AbstractUser):
            return user_to_json(instance)
        return instance.to_json()


class BaseListModelMixin(BaseModelView):

    search_fields = []
    filter_fields = []
    ordering = ["id"]

    def dispatch(self, request, *args, **kwargs):
        if not self.model:
            raise NotImplementedError("model cannot be empty.")
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self, request, **kwargs):
        return self.model.objects.all().order_by(*self.ordering)

    def filter_queryset(self, request, **kwargs):
        queryset = self.get_queryset(request, **kwargs)
        queryset = self.filter_by_fields(request, queryset)
        queryset = self.filter_by_search(request, queryset)
        return queryset

    def filter_by_search(self, request, queryset):
        search = request.GET.get("search", None)
        if search:
            if self.search_fields:
                query = functools.reduce(
                    lambda a, b: a | b, [models.Q(**{f"{field}__contains": search}) for field in self.search_fields]
                )
                queryset = queryset.filter(query)
            else:
                queryset = queryset.none()
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

    def to_results(self, request, instances):
        results = [self.model_to_json(request, instance) for instance in instances]
        return results

    def get(self, request, *args, **kwargs):
        queryset = self.filter_queryset(request, **kwargs)

        count = queryset.count()
        # 分页返回
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 20))
        paginator = Paginator(queryset, page_size)

        results = self.to_results(request, paginator.get_page(page))

        return JsonResponse({"count": count, "results": results}, status=HTTPStatus.OK)


class BaseCreateModelMixin(BaseModelView):

    def post(self, request, *args, **kwargs):
        data = self.parese_request_body(request)
        instance = self.model(**data)
        instance.full_clean()
        instance.save()
        return JsonResponse(self.model_to_json(request, instance), status=HTTPStatus.CREATED)


class BaseGenericModelMixin(BaseModelView):

    model = None
    pk_field = None

    @classmethod
    def get_object(cls, pk):
        if cls.pk_field and pk and not pk.isdigit():
            node = get_object_or_404(cls.model, **{cls.pk_field: pk})
        else:
            node = get_object_or_404(cls.model, pk=pk)
        return node


class BaseRetrieveModelMixin(BaseGenericModelMixin):

    def get(self, request, *args, pk=None, **kwargs):
        instance = self.get_object(pk)
        return JsonResponse(self.model_to_json(request, instance), status=HTTPStatus.OK)


class BaseUpdateModelMixin(BaseGenericModelMixin):

    def patch(self, request, *args, pk=None, **kwargs):
        instance = self.get_object(pk)

        data = self.parese_request_body(request)
        for k, v in data.items():
            setattr(instance, k, v)
        instance.full_clean()
        instance.save()
        return JsonResponse(self.model_to_json(request, instance), status=HTTPStatus.OK)


class BaseDestoryModelMixin(BaseGenericModelMixin):
    def delete(self, request, *args, pk=None, **kwargs):
        instance = self.get_object(pk)

        data = self.model_to_json(request, instance)
        instance.delete()
        return JsonResponse(data, status=HTTPStatus.NO_CONTENT)
