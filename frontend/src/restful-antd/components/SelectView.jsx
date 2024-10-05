import React, { useState, useEffect, useMemo, useCallback } from 'react';
import PropTypes from 'prop-types';
import { Select, Spin } from 'antd';
import {dequal as deepEqual} from 'dequal';

import { useProtect } from '../hooks';
import requests from '../requests';

const _parseListResponse = (data) => data?.results || [];

const SelectView = ({
  value,
  onChange,

  restful,
  genDetailUri = null,
  filters = null,
  searchKey = "search",
  parseListResponse = _parseListResponse,
  initOptions,

  fieldNames,
  // labelKey = 'label',
  // labelMethod,
  // valueKey = 'value',
  // valueMethod,

  disabled = false,
  mode,
  antdSelectProps = {},
}) => {

  const [protect] = useProtect();

  // 是否多选
  const [isMultiple, setMultiple] = useState(mode === 'multiple');
  // 选中的值
  const [innerValue, setInnverValue] = useState(value);
  // 远程搜索，用户输入的关键字
  const [searchValue, setSearchValue] = useState();
  const [loading, setLoading] = useState(false);
  // 下拉选项列表
  const [innerOptions, setInnerOptions] = useState(initOptions || []);

  const getOptionValue = useCallback((item) => item[fieldNames?.value || 'value'], [fieldNames]);

  const onValueChange = useCallback((value, option) => {
    setInnverValue(value);
    if (typeof onChange === 'function') {
      onChange(value, option);
    }
  }, [onChange]);

  // 初始化是否多选
  useEffect(() => {
    setMultiple(mode === 'multiple')
  }, [mode])

  // 初始化值
  useEffect(() => {
    setInnverValue((oldValue) => {
      if (deepEqual(oldValue, value)) {
        return oldValue;
      }
      return value;
    });
  }, [value]);

  // 被选中的值
  const selectedValues = useMemo(() => {
    if (innerValue === null || innerValue === undefined) {
      return [];
    }
    if (isMultiple) {
      return innerValue;
    }
    return [innerValue];
  }, [innerValue, isMultiple]);

  // 首次初始化
  useEffect(() => {
    if (isMultiple) {
      // 暂不支持多选
      return
    }
    if (innerValue === null || innerValue === undefined || innerValue === "") {
      return
    }
    // 初始化已被选中的options
    const values = isMultiple ? innerValue : [innerValue];
    const optValues = innerOptions.map(opt => getOptionValue(opt));
    // 没有options的选中项
    const fetchValues = values.filter(v => !optValues.includes(v));
    if (!fetchValues.length) {
      return
    }
    console.log("fetchValues==>", fetchValues)
    // 根据restful接口获取详情数据初始化options
    const promiseArr = fetchValues.map(v => requests.get(typeof genDetailUri === 'function' ? genDetailUri(v) : `${restful}${v}/`));
    Promise.all(promiseArr).then(protect(respArr => {
      const _options = respArr.map(resp => resp.data);
      setInnerOptions((oldOpts) => {
        return _options.concat(oldOpts);
      });
    }));
  }, [getOptionValue, innerValue, protect, isMultiple, restful, genDetailUri, innerOptions]);

  useEffect(() => {
    // 搜索值变化时
    if (disabled || !restful || !searchValue) {
      return;
    }
    const timer = setTimeout(protect(() => {
      let params = {...filters};
      if (searchValue) {
        params[searchKey] = searchValue;
      }
      setLoading(true);
      requests.get(restful, { params })
        .then(protect(response => {
          const results = parseListResponse(response.data);
          setInnerOptions((oldOpts) => {
            const selectedOpts = oldOpts.filter(opt => selectedValues.includes(getOptionValue(opt)));
            const _values = oldOpts.map(opt => getOptionValue(opt));
            const addOpts = results.filter(opt => !_values.includes(getOptionValue(opt)));
            return selectedOpts.concat(addOpts);
          });
        }), protect(() => {})).finally(protect(() => setLoading(false)));
    }), 200);
    return () => clearTimeout(timer);
  }, [restful, filters, searchKey, parseListResponse, searchValue, protect, disabled, selectedValues, getOptionValue]);

  const notFoundView = useMemo(() => {
    let _view = '无更多数据';
    if (restful) {
      if (loading) {
        _view = <Spin size="small"/>;
      } else {
        _view = '请输入合适的关键字进行搜索';
      }
      return _view;
    }
  }, [restful, loading]);

  return (
    <Select
      notFoundContent={notFoundView}
      popupMatchSelectWidth={false}
      allowClear={true}
      placeholder="可输入关键内容搜索，从下拉列表中选择"
      {...antdSelectProps}
      mode={mode}
      options={innerOptions}
      fieldNames={fieldNames}
      value={innerValue}
      showSearch={true}
      onSearch={(v) => setSearchValue(v)}
      onClear={() => onValueChange(null)}
      onSelect={(value, option) => onValueChange(value, option)}
    />
  );
};

SelectView.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,

  // 远程获取数据的接口
  restful: PropTypes.string.isRequired,
  genDetailUri: PropTypes.func,
  // 接口刷选条件
  filters: PropTypes.object,
  // 模糊搜索使用的key
  searchKey: PropTypes.string,
  parseListResponse: PropTypes.func,
  initOptions: PropTypes.arrayOf(PropTypes.object),

  fieldNames: PropTypes.object,

  // 默认单选，多选：multiple
  mode: PropTypes.string,
  // antd原生配置项
  antdSelectProps: PropTypes.object,

};

export default SelectView;
