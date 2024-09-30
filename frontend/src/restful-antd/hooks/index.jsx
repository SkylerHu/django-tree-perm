import { useCallback, useEffect, useRef } from 'react';

/**
 *  主要用于数据请求时
 */
export function useProtect () {

  const callbackRef = useRef({});
  const countRef = useRef(0);

  const noop = (...values) => values;

  const wrapCallback = useCallback((id) => {
    const myFunc = (...params) => {
      if (!callbackRef.current)
        return noop(...params);

      const callback = callbackRef.current[id];
      delete callbackRef.current[id];
      return callback(...params);
    }
    return myFunc;
  }, []);

  const protect = useCallback((callback) => {
    if (!callbackRef.current)
      return noop;

    const id = countRef.current++;
    callbackRef.current[id] = callback;

    return wrapCallback(id);
  }, [wrapCallback]);

  useEffect(() => {
    callbackRef.current = {};
    return () => {
      callbackRef.current = null;
    };
  }, []);

  return [protect];
}
