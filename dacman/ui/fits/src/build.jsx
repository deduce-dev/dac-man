
import React, { useContext, useState, useReducer } from 'react';

import {
  useStyles,
  WorkbenchCard,
  PrettyPrinter,
 } from './Layout';

import {
  getResponse,
} from './api';

import {
  Typography,
  Button,
  FormControl,
  Select,
  MenuItem,
  FormHelperText,
  Grid,
  Container,
  FormControlLabel,
  Checkbox,
} from '@material-ui/core';

// given a stage, get the next one
// TODO this sort of mocks the interaction with the backend,
// and is independent of any dispatch/reducer logic
// so in principle could be moved somewhere else
function getNextStage(stageKey) {
  switch (stageKey) {
    case null:
      return {
        action: 'display',
        resource: 'dir',
        stageKey: 'select/dir',
        paramSpecs: [
          {
            paramKey: 'dir.A',
            resource: 'dir',
            compareSide: 'A',
            defaultValue: '/foo/bar/',
          },
          {
            paramKey: 'dir.B',
            resource: 'dir',
            compareSide: 'B',
            defaultValue: '/biz/baz/'
          },
        ]
      };
    case 'select/dir':
      return {
        action: 'select',
        resource: 'file',
        stageKey: 'select/file',
        description: "Select the two files to compare",
        paramSpecs: [
          {
            paramKey: 'file.A',
            resource: 'file',
            compareSide: 'A',
            sourceSpec: {resource: 'dir', paramKey: 'dir.A'},
            defaultValue: '',
          },
          {
            paramKey: 'file.B',
            resource: 'file',
            compareSide: 'B',
            sourceSpec: {resource: 'dir', paramKey: 'dir.B'},
            defaultValue: ''
          },
        ]
      };
    case 'select/file':
      // TODO also in this case, we assume this is by default FITS
      // but in reality we should get the real values from the backend
      return {
        action: 'select',
        resource: 'fits.hdu',
        stageKey: 'select/fits.hdu',
        description: "Select the two HDUs to compare",
        paramSpecs: [
          {
            resource: 'fits.hdu',
            compareSide: 'A',
            paramKey: 'fits.hdu.A',
            sourceSpec: {resource: 'file', paramKey: 'file.A'},
            defaultValue: {}
          },
          {
            resource: 'fits.hdu',
            compareSide: 'B',
            paramKey: 'fits.hdu.B',
            sourceSpec: {resource: 'file', paramKey: 'file.B'},
            defaultValue: {}
          },
        ]
      };
    case 'select/fits.hdu':
      return {
        stageKey: 'set/anaopts',
        description: "Set the values for the change analysis options",
        isLast: true,
        paramSpecs: [
          {
            paramKey: 'anaopts.normalize',
            type: 'bool',
            defaultValue: true,
          },
          {
            paramKey: 'anaopts.visualization',
            type: 'text',
            choices: ['histogram', 'heatmap'],
            defaultValue: 'histogram'
          }
        ]
      };
    default:
      break;
  }
}

// actions
const ACTIONS = {
  ADVANCE_STAGE: 'ADVANCE_STAGE',
  ADD_STAGE: 'ADD_STAGE',
  REMOVE_STAGE: 'REMOVE_STAGE',
  RESET_STAGES: 'RESET_STAGES',
};

// action creators
export function advanceStage(stageKey) {
  return {
    type: ACTIONS.ADVANCE_STAGE,
    payload: {
      currentStageKey: stageKey,
    }
  };
}

export function addStage(stageData) {
  return {
    type: ACTIONS.ADD_STAGE,
    payload: {...stageData}
  };
}

export function resetStages() {
  return {
    type: ACTIONS.RESET_STAGES,
  };
}


function stagesReducer(state, action) {
  switch (action.type) {
    case ACTIONS.ADVANCE_STAGE:
      const next = getNextStage(action.payload.currentStageKey);
      // TODO dispatch setting of paramvalues from new stage paramkeys here?
      // or maybe it would be better to do it in the stage component?
      return [
        ...state,
        next
      ];
    case ACTIONS.ADD_STAGE:
      return [
        ...state,
        action.payload,
      ];
    case ACTIONS.RESET_STAGES:
      // TODO maybe call initStages instead
      return [
        getNextStage(null)
      ];
    default:
      break;
  }
}

export const StagesContext = React.createContext([]);
export const StagesDispatchContext = React.createContext(undefined);

export function StagesContextProvider({ children }) {
  const [stages, stagesDispatch] = useReducer(
    stagesReducer,
    null,
    () => { return [getNextStage(null)]; }
  );

  return (
    <StagesContext.Provider value={stages}>
      <StagesDispatchContext.Provider value={stagesDispatch}>
        {children}
      </StagesDispatchContext.Provider>
    </StagesContext.Provider>
  );
}

export const ParamsContext = React.createContext({});
export const ParamsDispatchContext = React.createContext(undefined);

export function ParamsContextProvider({ children }) {
  const [params, paramsDispatch] = useReducer(
    paramsReducer,
    null,
    // TODO this should be changed with a more meaningful set of initial params
    () => {
      return {};
    }
  );
  return (
    <ParamsContext.Provider value={params}>
      <ParamsDispatchContext.Provider value={paramsDispatch}>
        {children}
      </ParamsDispatchContext.Provider>
    </ParamsContext.Provider>
  );
}

// param actions
const PARAMS_ACTIONS = {
  SET_VALUE: 'SET_VALUE',
  SET_DEFAULT_VALUE: 'SET_DEFAULT_VALUE',
};


// param action creators
function setParamValue(paramKey, value) {
  return {
    type: PARAMS_ACTIONS.SET_VALUE,
    payload: {
      paramKey: paramKey,
      value: value
    }
  };
}

function setParamDefaultValue(paramSpec) {
  return {
    type: PARAMS_ACTIONS.SET_DEFAULT_VALUE,
    payload: {
      paramKey: paramSpec.paramKey,
      defaultValue: paramSpec.defaultValue,
    }
  };
}

function paramsReducer(state, action) {
  switch (action.type) {
    case PARAMS_ACTIONS.SET_VALUE:
      return {
        ...state,
        [action.payload.paramKey]: action.payload.value,
      };
    case PARAMS_ACTIONS.SET_DEFAULT_VALUE:
      const paramKey = action.payload.paramKey;
      const currentValue = state[paramKey];
      return {
        ...state,
        [paramKey]: (currentValue === undefined) ? action.payload.defaultValue : currentValue, 
      };
    default:
      break;
  }
};

function useParam(paramKey, defaultValue = null) {
  const value = useContext(ParamsContext)[paramKey];
  const dispatch = useContext(ParamsDispatchContext);
  // TODO this might eventually need some useCallback/React.memo
  const setValue = React.useCallback(
    (val) => {
      dispatch(setParamValue(paramKey, val));
    },
    [paramKey]
  );
  // console.log(`useParam: paramKey: ${paramKey} value: ${value}`)
  // if (value === undefined) {
  //   console.log(`Setting param value from ${value} to ${defaultValue}`)
  //   setValue(defaultValue);
  // }

  // TODO we could also set the initial param value here
  // using setValue if this function is called with an optional argument?
  return [
    value,
    setValue
  ];
}

function DisplayDir(paramSpec) {
  console.log('DisplayDir.paramSpec'); console.log(paramSpec);
  const [value, setParam] = useParam(paramSpec.paramKey, paramSpec.defaultValue);
  return (
    <Typography>
      <code>
        {value || paramSpec.defaultValue}
      </code>
    </Typography>
  );
}

function SelectDirsStage({ stage }) {
  console.log('SelectDirsStage.stage'); console.log(stage);
  return (
    <>
      {stage.paramSpecs.map((spec, idx) => <DisplayDir key={idx} {...spec} />)}
    </>
  );
}

function SelectFile(paramSpec) {
  const {
    paramKey,
    description,
    ...spec
  } = paramSpec;
  const defaultValue = '';
  const [paramValue, setParamValue] = useParam(paramKey);
  const handleChange = (e) => {
    setParamValue(e.target.value);
  };

  const [choices, setChoices] = useState([paramValue]);

  // console.log('SelectFile.choices'); console.log(choices);
  // console.log('SelectFile.paramValue'); console.log(paramValue);

  // React.useEffect(
  //   () => {
  //   if (paramValue === undefined) {
  //     console.log(`Setting param value from ${paramValue} to ${defaultValue}`)
  //     setParamValue(defaultValue);
  //     }
  //   },
  //   []
  // );
  
  const renderChoices = (item, index) => {
    return (
      <MenuItem key={index} value={item}>
       {item}
      </MenuItem>
    )
  };

  const sourceSpec = paramSpec.sourceSpec;
  const [sourceValue, _ignore] = useParam(sourceSpec.paramKey);

  const updateChoices = () => {
    const respData= getResponse('get_content', {resource: sourceSpec.resource, value: sourceValue});
    const newChoices = respData.values;
    setChoices(newChoices);
  };

  return (
    <FormControl>
      <Select
        variant="outlined"
        value={paramValue}
        onChange={handleChange}
        onOpen={(e) => updateChoices()}
        // renderValue={(item) => <MenuItem key={item} value={item}>{item}</MenuItem>}
      >
        {choices.map(renderChoices)}
      </Select>
      <FormHelperText>{description}</FormHelperText>
    </FormControl>
  );
}

function SelectFilesStage({ stage }) {
  return (
    <>
      {stage.paramSpecs.map((spec, idx) => <SelectFile key={idx} {...spec} />)}
    </>
  )
};

function SelectFITSHDU(paramSpec) {
  const {
    paramKey,
    description,
    ...spec
  } = paramSpec;
  const [paramValue, setParamValue] = useParam(paramKey);
  const handleChange = (e) => {
    setParamValue(e.target.value);
  };

  const [choices, setChoices] = useState([paramValue]);
  const renderChoices = (item, index) => {
    return (
      <MenuItem key={index} value={item}>
       {JSON.stringify(item)}
      </MenuItem>
    )
  };

  const sourceSpec = paramSpec.sourceSpec;
  const [sourceValue, _ignore] = useParam(sourceSpec.paramKey);

  const updateChoices = () => {
    const respData= getResponse('get_content', {resource: sourceSpec.resource, value: sourceValue});
    const newChoices = respData.values;
    setChoices(newChoices);
  };

  return (
    <FormControl>
      <Select
        variant="outlined"
        value={paramValue}
        onChange={handleChange}
        onOpen={(e) => updateChoices()}
      >
        {choices.map(renderChoices)}
      </Select>
      <FormHelperText>{description}</FormHelperText>
    </FormControl>
  );
}

function renderChoices(item, index) {
  return (
    <MenuItem key={index} value={item}>
      {JSON.stringify(item)}
    </MenuItem>
  );
}

function SelectFITSHDUsStage({ stage }) {
  return (
    <>
      {stage.paramSpecs.map((spec, idx) => <SelectFITSHDU key={idx} {...spec} />)}
    </>
  )
}

function SelectGeneric(paramSpec) {
  const {
    paramKey: key,
    description,
    type,
    choices,
  } = paramSpec;
  const [value, setValue] = useParam(key);
  
  if (choices !== undefined) {
    return (
      <FormControl>
        <Select
          variant="outlined"
          value={value}
          onChange={(e) => setValue(e.target.value)}
        >
          {choices.map(renderChoices)}
        </Select>
      </FormControl>
    );
  }
  else if (type === 'bool') {
    return (
      <FormControlLabel
        control={
          <Checkbox
            checked={value}
            onChange={(e) => setValue(e.target.checked)}
          />
        }
        label={description || "No description available"}
        helperText="Some helper text that I'm adding here"
      />
    )
  };
}

function SetAnaOptsStage({ stage }) {
  return (
    <>
      {stage.paramSpecs.map((spec, index) => <SelectGeneric key={index} {...spec} />)}
    </>
  )
}

// TODO decide if it makes more sense to have the switch at the level
// of the entire stage or at the single param/paramSpec
function getParamComponent(params) {
  return;
}

function getStageComponent(stage) {
  console.log('getStageComponent.stage'); console.log(stage);
  switch (stage.stageKey) {
    case 'select/dir':
      return SelectDirsStage;  
    case 'select/file':
      return SelectFilesStage;
    case 'select/fits.hdu':
      return SelectFITSHDUsStage;
    case 'set/anaopts':
      return SetAnaOptsStage;
    default:
      return (stage) => {return <PrettyPrinter item={stage} />};
      // return (
      //   <>
      //     {stage.paramSpecs.map(DisplayDir)}
      //   </>
      // );
  };
}

function NextControls({ stage }) {
  const stagesDispatch = useContext(StagesDispatchContext);
  const paramsDispatch = useContext(ParamsDispatchContext);
  // TODO to dispatch the final action here, we could use another (comparison-level) context
  // alternatively, depending on how much we would end up using it elsewhere,
  // we could simply have the caller pass it to this component
  const setParamDefaultValues = (stage) => {
    stage.paramSpecs.forEach((spec) => {
        paramsDispatch(setParamDefaultValue(spec));
      }
    );
  }
  let handleClick = (e) => {
    // setParamDefaultValues() will be called twice for each stage other than the first and the last,
    // but it's supposed to be idempotent so in first approx it shouldn't be an issue
    setParamDefaultValues(stage);
    const next = getNextStage(stage.stageKey);
    console.log('NextControls.next'); console.log(next);
    stagesDispatch(addStage(next));
    setParamDefaultValues(next);
  };
  let label = 'Next';

  if (stage.isLast) {
    handleClick = (e) => alert('This would dispatch running the built comparison!');
    label = 'Run comparison';
  };

  return (
    <Button
      variant="contained"
      color="primary"
      onClick={handleClick}
    >
      {label}
    </Button>
  );
}

function getWorkbenchCard(stage, index) {
  const StageComponent = getStageComponent(stage);
  return (
    <>
      <WorkbenchCard
        key={`card-${stage.stageKey}`}
        title={`Stage #${index}`}
      >
        <Typography>{stage.description}</Typography>
        <StageComponent key={stage.stageKey} stage={stage} />
      </WorkbenchCard>
    </>
  );
}

function ShowParams(props) {
  const params = useContext(ParamsContext);
  return (
    <PrettyPrinter item={params} />
  );
}

export function SlimComparisonBuilder(props) {
  const stages = useContext(StagesContext);
  const dispatch = useContext(StagesDispatchContext);

  console.log('SlimComparisonBuilder.stages'); console.log(stages);

  return (
    <>
      <Typography variant="h4">{`Number of stages: ${stages.length}`}</Typography>
        <Button
          variant="contained"
          color="primary"
          onClick={e => dispatch(resetStages())}
        >
          Reset
        </Button>
      <Grid container spacing={3}>
        {stages.map(getWorkbenchCard)}
      </Grid>
      {stages.slice(-1).map(stage => <NextControls key={`next-after-${stage.stageKey}`} stage={stage} />)}
      <ShowParams />
    </>
  );
}

// TODO this should be in Layout.jsx
export function WorkbenchContainer({ children }) {
  const classes = useStyles();

  return (
    <main className={classes.content}>
      <div className={classes.toolbar} />
      <Container maxWidth="lg" className={classes.container}>
        {children}
      </Container>
    </main>
  );
} 