export function formatObjToStr (item, show, sub = null) {
  let label = "";
  if (!item || typeof item === "string") {
    label = item;
  } else if (item && item instanceof Object) {
    label = item[show];
    if (!label) {
      // 若是主要的展示没有，展示id即可
      label = `(id:${item.id})`;
    }
    if (sub && item[sub]) {
      label = `${label} (${item[sub]})`;
    }
  }
  return label;
}

export function formatObjFromKeys (item, keys) {
  let label = formatObjToStr(item, ...keys.slice(0, 2));
  if (item instanceof Object && keys && keys.length > 2) {
    label += keys.slice(2).map(key => ` (${item[key]})`).join("");
  }
  return label;
}

export function getItemLabel (item, { labelKey, labelMethod }) {
  let v = item;
  if (item && item instanceof Object) {
    if (labelKey) {
      if (labelKey instanceof Array) {
        v = formatObjFromKeys(item, labelKey);
      } else {
        v = formatObjToStr(item, labelKey);
      }
    } else if (typeof labelMethod === "function") {
      v = labelMethod(item);
    } else {
      v = item.label || item.name || item.title;
    }
  }
  console.log("label=>", item, v)
  return v;
}

export function getItemValue (item, { valueKey, valueMethod }) {
  let v = item;
  if (item && item instanceof Object) {
    if (valueKey === "string") {
      v = item[valueKey];
    } else if (valueMethod === "function") {
      v = valueMethod(item);
    } else {
      v = item.id || item.value;
    }
  }
  console.log("value=>", item, v)
  return v;
}
