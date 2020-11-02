import update from 'immutability-helper';
import React, { useReducer } from 'react';


function getFiles() {
    const data = [
        {
            path: '/foo/bar/baz',
            key: '/foo/bar/baz',
            isDir: true
        },
        {
            path: '/foo/bar/baz/base.fits',
            key: '/foo/bar/baz/base.fits',
            type: 'fits'
        },
        {
            path: '/foo/bar/baz/base.csv',
            key: '/foo/bar/baz/base.csv',
            type: 'csv'
        },
        {
            path: '/foo/bar/baz/base.hdf5',
            key: '/foo/bar/baz/base.hdf5',
            type: 'hdf5',
        },
    ];

    return data;
}

function getFitsHDUs() {
    return {
        A: [
            {
                extension: 0,
                name: 'PRIMARY',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
                content_type: 'spectrum'
            },
            {
                extension: 1,
                name: 'IVAR',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
            },
            {
                extension: 2,
                name: 'PLUGMAP',
                hdu_type: 'BinTable',
                dimensions: '1000r x 35c',
            },
        ],
        B: [
            {
                extension: 0,
                name: 'PRIMARY',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
                content_type: 'spectrum'
            },
            {
                extension: 1,
                name: 'IVAR',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
            },
        ]
    }
}

function getComparisonCSV(id) {
    return {
        comparisonID: id,
        type: "csv",
        layers: [
            {
                type: "file",
                path: {
                    A: "base.csv",
                    B: "new.csv"
                },
            },
        ]
    }
}

function getComparisonFITS(id) {

    return {
        comparisonID: id,
        type: "fits",
        layers: [
            {
                type: "file",
                path: {
                    A: "space-data-v33.fits",
                    B: "space-data-v34.fits"
                },
            },
            {
                type: "fits",
                contents: getFitsHDUs(),
            }
        ]
    }
}

function getComparisonHDF5(id) {
    return {
        comparisonID: id,
        type: "hdf5",
        layers: [
            {
                type: "file",
                path: {
                    A: "sample-2019-11-01.h5",
                    B: "sample-2020-05-05.h5"
                },
            },
        ],
        results: [
            {
                type: "counts",
                data: {
                    total: 4452,
                    added: 123,
                    deleted: 45,
                    modified: 12,
                    unchanged: 3523,
                },
                // foo: "bar"
            },
            {
                type: "heatmap",
                data: {
                    url: '/base/delta.png'
                }
            }
        ]
    }
}

function getComparisonGeneric(id, type, names) {

    return {
        comparisonID: id,
        type: type,
        layers: [
            {
                type: "file",
                path: {
                    A: `${names[0]}.${type}`,
                    B: `${names[1]}.${type}`,
                },
            }
        ]
    }
}

function getComparisons() {
    return [
        getComparisonCSV(1),
        getComparisonFITS(2),
        getComparisonHDF5(3),
        getComparisonGeneric(4, "txt", ["data-v1", "data-v2"])
    ];
}

function getDirContentsFromComparisons() {
    let res = {A: [], B: []};
    let cmps = getComparisons();
    let getBrowserProperties = (p) => {
        return {
            path: p,
            key: p,
            isDir: false
        }
    }
    cmps.forEach(
        cmp => {
            let paths = getLayer(cmp, "file").path;
            res.A.push(getBrowserProperties(paths.A));
            res.B.push(getBrowserProperties(paths.B));
        }
    )

    return res;
}

function getCommonLayers() {
    let layers = [
        {
            type: "dir",
            labels: {
                A: "/path/to/dir",
                B: "/some/other/dir"
            },
            contents: getDirContentsFromComparisons(),
        }
    ];
    return layers;
}

function getComparisonByID(id) {
    let cmps = getComparisons();
    console.log('All comparisons:'); console.log(cmps);
    id = parseInt(id);
    console.log('Requested id:'); console.log(id);
    let found = cmps.find(c => c.comparisonID === id);
    console.log('typeof(id):'); console.log(typeof(id));
    console.log('Found:'); console.log(found);
    // for the time being, create a shallow copy
    return {...found};
}

function getLayer(cmp, type) {

    return cmp.layers.find(l => l.type === type);
}


function getLayersFromDir(cid, params) {
    let layers = [];
    // let cmp = getComparisonByID(cid);
    // let dirLayer = getLayer(cmp, "dir");
    // let sel = {
    //     A: dirLayer.content.A[params.selected.A],
    //     B: dirLayer.content.B[params.selected.B]
    // };
    let {selected, ...otherParams} = params;
    let fileLayer = {
        type: "file",
        path: {
            A: selected.A.path,
            B: selected.B.path,
        }
    };
    layers.push(fileLayer);

    if (selected.A.type === selected.B.type) {
        let type = selected.A.type;
        let fileContentLayer = {
            type: type
        }
        switch (type) {
            case "fits":
                fileContentLayer.contents = getFitsHDUs();
                break;
        };
        layers.push(fileContentLayer);
    }

    return layers;
}


function getLayersFromHDUSelection(cid, params) {
    let layer = {
        type: 'fits_hdu',
        supports: [],
    };
    let {selected, ...otherParams} = params;

    if (selected.A.hdu_type === selected.B.hdu_type) {
        switch (selected.A.hdu_type) {
            case "Image":
                layer.supports.push(
                    {
                        name: "arrayB - arrayA",
                        visualizations: [
                            "histogram",
                            "heatmap"
                        ]
                    }
                );
                break;
        };
    }
    return [layer];
}


function getNextLayer(cid, currLayer) {
    
}


// this simulates an actual call to the backend
export function getResponse(action, params) {
  if (action === "get_content") {
    const {resource, value, ...other} = params;
    let response = {
      request: {...params}
    };
    if (resource === "dir") {
      return {
        ...response,
        resource: "file",
        values: [
          'mercury.fits',
          'venus.fits',
          'mars.fits',
        ]
      }
    };
    if (resource === "file") {
      return {
        ...response,
        // TODO this is hard-coded here temporarily
        // the resource should actually be detected by the plugin
        resource: "fits.hdu",
        values: [
            {
                extension: 0,
                name: 'PRIMARY',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
                content_type: 'spectrum'
            },
            {
                extension: 1,
                name: 'IVAR',
                hdu_type: 'Image',
                dimensions: '(4645, 1000)',
            },
            {
                extension: 2,
                name: 'PLUGMAP',
                hdu_type: 'BinTable',
                dimensions: '1000r x 35c',
            },
        ]
      }
    }
  } else if (action === "get_analysis_params") {

  } else {};

}

function getNextStage(prev = null, formData = {}) {
  let next = {};
  console.log('getNextStage.prev:');
  console.log(prev)
    if (prev === null) {
    //   next = {
    //     action: "select",
    //     resource: "dir",
    //     description: "Select the dirs to compare"
    //   };
    // }
    // else if (prev.action === "select" && prev.resource === "dir") {
      let src = {
        A: formData["dir.A"],
        B: formData["dir.B"]
      }
      let resp = {};
      resp.A = getResponse('get_content', {resource: 'dir', value: src.A});
      resp.B = getResponse('get_content', {resource: 'dir', value: src.B});
      next = {
        action: "select",
        resource: "file",
        description: "Select the two files to compare",
        choices: {
          A: resp.A.values,
          B: resp.B.values,
        },
        source: {...src},
        selected: {
          A: null,
          B: null
        },
        buildParams: [
          {
            key: 'file.A',
            resource: 'file',
            compareSide: 'A',
            getChoices: () => getResponse('get_content', {resource: 'dir', value: src.A}),
            choices: getResponse('get_content', {resource: 'dir', value: src.A}),
            source: {resource: 'dir', value: src.A},
            value: '',
          },
          {
            key: 'file.B',
            resource: 'file',
            compareSide: 'B',
            getChoices: () => getResponse('get_content', {resource: 'dir', value: src.B}),
            choices: getResponse('get_content', {resource: 'dir', value: src.B}),
            source: {resource: 'dir', value: src.B},
            value: '',
          }
        ]
      };
    }
    else if (prev.action === "select" && prev.resource === "file") {
      let src = {
        A: formData["file.A"],
        B: formData["file.B"]
      }
      let resp = {};
      resp.A = getResponse('get_content', {resource: 'file', value: src.A});
      resp.B = getResponse('get_content', {resource: 'file', value: src.B});
      next = {
        action: "select",
        resource: "fits.hdu",
        plugin: "FITSPlugin",
        description: "Select the two HDUs to compare",
        choices: {
          A: resp.A.values,
          B: resp.B.values,
        },
        source: {...src},
        selected: {
          A: null,
          B: null,
        },
        buildParams: [
          {
            key: 'fits.hdu.A',
            resource: 'fits.hdu',
            compareSide: 'A',
            getChoices: () => getResponse('get_content', {resource: 'file', value: src.A}),
            choices: getResponse('get_content', {resource: 'file', value: src.A}),
            source: {resource: 'file', value: src.A},
            value: '',
          },
          {
            key: 'fits.hdu.B',
            resource: 'fits.hdu',
            compareSide: 'B',
            getChoices: () => getResponse('get_content', {resource: 'file', value: src.B}),
            choices: getResponse('get_content', {resource: 'file', value: src.B}),
            source: {resource: 'file', value: src.B},
            value: '',
          }
        ]
      };
    }
    else {
      next = {
        action: "set_parameters",
        resource: "analysis_params",
        description: "Select the analysis parameters",
        isLast: true,
        selected: {
          normalize: true
        },
        buildParams: [
          {
            key: 'analysisParams.normalize',
            type: 'bool',
            value: true,
          },
          {
            key: 'analysisParams.visualization',
            type: 'string',
            choices: ['histogram', 'heatmap'],
            value: '',
          }
        ]

      };
    };

    return next;
}

// reducer actions
export const ACTIONS = {
  ADD_BUILD_STAGE: 'ADD_BUILD_STAGE',
  RESET_BUILD_STAGES: 'RESET_BUILD_STAGES',
  SET_FORM_DATA: 'SET_FORM_DATA',
  SUBMIT_FORM_DATA: 'SUBMIT_FORM_DATA',
  SET_BUILD_PARAM_VALUE: 'SET_BUILD_PARAM_VALUE',
  SET_BUILD_PARAM: 'SET_BUILD_PARAM',
};

function buildComparisonReducer(state, action) {

  console.log('inside buildComparisonReducer');
  switch (action.type) {
    case 'setFormData':
      return {
        ...state,
        formData: {
          ...state.formData,
          [action.name]: action.value
        }
      };
    case 'resetStages':
      console.log('dispatching resetStages');
      return initBuildState(state.onFormDataComplete);
    case 'addStage':
      const stages = state.stages;
      // const toCheck = stages.slice(-1)[0];
      const toCheck = action.currentStage;
      const toBeAdded = getNextStage(toCheck, state.formData);
      console.log('[reducer]addStage.stages:'); console.log(stages);
      console.log('[reducer]addStage.toCheck:'); console.log(toCheck);
      return {
        ...state,
        stages: [
          ...stages, toBeAdded
        ]
      };
    case 'sendFormData':
      // not sure if calling this function here is a violation of the reducer principles
      // in any case it's only here temporarily, since the reducer itself should be lifted up into the parent component
      state.onFormDataComplete(state.formData);
      return initBuildState(state.onFormDataComplete);
    case ACTIONS.SET_BUILD_PARAM_VALUE:
      const key = action.payload.key;
      const param = state.buildParamsByKey[key];
      return {
        ...state,
        buildParamsByKey: {
          ...state.buildParamsByKey,
          [key]: {
            ...param,
            value: action.payload.value
          }
        }
      };
  default:
    return state;
  };
}

function initBuildState(onFormDataComplete) {
  return {
    stages: [getNextStage()],
    formData: {
      "dir.A": "/data/solar-system-v1/",
      "dir.B": "/data/solar-system-v2/",
    },
    onFormDataComplete: onFormDataComplete,
  };
}

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

function getNextBuildStage(prev = null, buildParams)  {
  let next = {};

  if (prev === null || prev.name === 'select/dir') {

    next = {

    }

  };
  return next;
}


function buildParamsReducer(state, action) {
  switch (action.type) {
    case ACTIONS.SET_BUILD_PARAM_VALUE:
      const key = action.payload.key;
      const param = state[key];
      return {
        ...state,
        [key]: {
          ...param,
          value: action.payload.value,
        }
      };
    case ACTIONS.SET_BUILD_PARAM:
      return {
        ...state,
        [action.payload.key]: {...action.payload.paramData}
      };
    default:
      return state
  }
}

function comparisonsReducer(state, action) {
  switch (action.type) {
    case 'addFromBuild':
      const buildData = action.buildData;
      let toAdd = {
        comparisonID: state.length + 1,
        calcStatus: 'processing',
        displayStatus: null,
        data: {
          file: {
            A: buildData["file.A"],
            B: buildData["file.B"]
          }
        }
      };
      return update(
        state,
        {$push: [toAdd]}
      );
      return [
        ...state,
        toAdd
      ];
  default:
    return state;
  };

}

export const BuildStateContext = React.createContext({});
export const BuildDispatchContext = React.createContext(undefined);

export const BuildContextProvider = ({ children }) => {
  const [buildState, buildDispatch] = useReducer(
    buildComparisonReducer,
    (formData) => {console.log(formData)},
    initBuildState
  );
  return (
    <BuildStateContext.Provider value={buildState}>
      <BuildDispatchContext.Provider value={buildDispatch}>
        {children}
      </BuildDispatchContext.Provider>
    </BuildStateContext.Provider>
  )
}

export const BuildParamsContext = React.createContext({});
export const BuildParamsDispatchContext = React.createContext(undefined);

export const BuildParamsContextProvider = ({ children }) => {
  const [params, paramsDispatch] = useReducer(
    buildParamsReducer,
  );
  return (
    <BuildParamsContext.Provider value={params}>
      <BuildParamsDispatchContext.Provider value={paramsDispatch}>
        {children}
      </BuildParamsDispatchContext.Provider>
    </BuildParamsContext.Provider>
  )
}

export {
    getComparisons,
    getComparisonByID,
    getComparisonGeneric,
    getLayer,
    getCommonLayers,
    buildComparisonReducer,
    // getNextLayer,
    // getNewComparisonBuildState,
    comparisonsReducer,
    initBuildState,
    // getNextStage,
    getComparisonHDF5,
};
