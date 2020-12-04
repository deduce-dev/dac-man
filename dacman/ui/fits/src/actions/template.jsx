
// action creators
export function setBuildParamValue(key, value) {
  return {
    type: ACTIONS.SET_BUILD_PARAM_VALUE,
    payload: {
      key: key,
      value: value
    }
  };
}

export function setBuildParam(key, paramData) {
  return {
    type: ACTIONS.SET_BUILD_PARAM,
    payload: {
      key: key,
      paramData: {...paramData}
    }
  };
}
