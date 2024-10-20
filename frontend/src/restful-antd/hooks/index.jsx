import { useEffect, useRef } from 'react';

function protectFromUnmount() {

  let callbacks = {};
  let count = 0;
  const noop = (...value) => value;

  const wrapCallback = id => function(...params) {
    const raceSafeCallbacks = callbacks;

    const callback = raceSafeCallbacks[id];
    delete raceSafeCallbacks[id];
    if (!callback) {
      return noop(...params);
    }
    return callback(...params);
  };

  const protect = (callback) => {
    const raceSafeCallbacks = callbacks;

    const id = count++;
    raceSafeCallbacks[id] = callback;
    return wrapCallback(id);
  };

  protect.unmount = () => callbacks = {};

  return protect;
}

/**
 *  主要用于数据请求时
 */
export function useProtect () {
  const protectRef = useRef(protectFromUnmount());

  useEffect(() => {
    protectRef.current = protectFromUnmount();
    return () => {
      protectRef.current && protectRef.current.unmount();
    };
  }, []);

  return [protectRef.current];
}
