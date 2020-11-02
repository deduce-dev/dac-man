import React, { useState, useContext } from 'react';

import {
  Container,
  Grid,
  Card,
  Typography
} from "@material-ui/core";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import MenuItem from "@material-ui/core/MenuItem";
import Select from "@material-ui/core/Select";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormGroup from "@material-ui/core/FormGroup";
import Checkbox from "@material-ui/core/Checkbox";

import MaterialTable from 'material-table';

import { useStyles, WorkbenchCard } from './Layout';
import { 
  BuildStateContext,
  BuildDispatchContext,
  BuildParamsContext,
  BuildParamsDispatchContext,
  setBuildParamValue,
  getResponse,
} from './api';


function getComponent(stage) {
  console.log('getComponent.stage:'); console.log(stage);
  if (stage.action === "select" && stage.resource === "dir") {
    return DirSelector;
  }
  else if (stage.action === "select" && stage.resource === "file") {
    return FileSelector;
  }
  else if (stage.action === "select" && stage.resource === "fits.hdu") {
    return FITSSelector;
  }
  else if (stage.action === "set_parameters") {
    return SelectAnalysisParams;
  }
  else return GenericSelector;
}

function NextControls({ stage, dispatch }) {
  let action = {
    type: 'addStage',
    currentStage: stage
  };
  let label = "Next";

  if (stage.isLast) {
    action = {
      type: 'sendFormData'
    }
    label = "Run comparison";
  }

  return (
    <Button
      variant="contained"
      color="primary"
      onClick={(e) => dispatch(action)}
    >
      {label}
    </Button>
  )
}

function ComparisonBuilder({ state, dispatch }) {
  const classes = useStyles();

  function getWorkbenchCard(stage, index) {
    const StageComponent = getComponent(stage);
    return (
      <>
        <WorkbenchCard
          key={`card-${index}`}
          title={`Step #${index}`}
        >
          <Typography>{stage.description}</Typography>
          <StageComponent key={index} stage={stage} dispatch={dispatch} />
        </WorkbenchCard>
      </>
    );
  }

  const InitialComponent = () => {
    return (
      <WorkbenchCard
        key="card-initial"
        title="Dirs under comparison"
      >
        <DirSelector dispatch={dispatch} />
      </WorkbenchCard>
    )
  };

  return (
    <main className={classes.content}>
      <div className={classes.toolbar} />
      <Container maxWidth="lg" className={classes.container}>
        <InitialComponent />
        <Typography variant="h4">{`Number of stages: ${state.stages.length}`}</Typography>
        <Button variant="contained" color="primary" onClick={e => dispatch({ type: 'resetStages' })}>Reset</Button>
        <Grid container spacing={3}>
          {state.stages.map(getWorkbenchCard)}
        </Grid>
        {state.stages.slice(-1).map(stage => <NextControls stage={stage} dispatch={dispatch} />)}
      </Container>
    </main>
  );
}

function GenericSelector({ stage, dispatch, resource = 'resource' }) {
  return (
    <div>
      <FormGroup column>
        <ChoiceSelector
          name={`${resource}.A`}
          description={`Choose ${resource} (A)`}
          choices={stage.choices.A}
          dispatch={dispatch}
        />
        <ChoiceSelector
          name={`${resource}.B`}
          description={`Choose ${resource} (B)`}
          choices={stage.choices.B}
          dispatch={dispatch}
        />
      </FormGroup>
    </div>
  );
}


function DirSelector({ stage, dispatch }) {
  // TODO: values are hardcoded, but should be taken from the stage
  return (
    <>
      <FixedSelector
        name="dir.A"
        value="/data/solar-system-v1/"
        dispatch={dispatch}
      />
      <br />
      <FixedSelector
        name="dir.B"
        value="/data/solar-system-v2/"
        dispatch={dispatch}
      />
    </>
  )
}


function FileSelector({ stage, dispatch }) {
  return (
    <div>
      <FormGroup column>
        <ChoiceSelector
          name="file.A"
          description="Choose file (A)"
          choices={stage.choices.A}
          dispatch={dispatch}
        />
        <ChoiceSelector
          name="file.B"
          description="Choose file (B)"
          choices={stage.choices.B}
          dispatch={dispatch}
        />
      </FormGroup>
    </div>
  );
}


function SingleFileSelector({paramKey, value, compareSide, source, dispatch, ...props}) {
  // at this point we could also do the API call here to get the choices
  // this could use useEffect specifying a dependency on source,
  // so that whenever source is changed, the values are fetched again (ideally...)
  return (
    <ChoiceSelector
      name={paramKey}
      value={value}
      description={`Choose file (${compareSide})`}
      choices={props.choices}
      dispatch={dispatch}
    />
  )
}

function SingleDirSelectorWithCtx({ paramKey }) {
  const param = useContext(BuildParamsContext)[paramKey];
  return (
    <Typography>
      <code>
        {param.value}
      </code>
    </Typography>
  );
}

function SingleFileSelectorWithCtx2({ paramKey, paramSpec, source }) {
  const [choices, setChoices] = useState([]); // or maybe use the value here as the default?
  // also: instead of using useEffect() (choices are fetched on render)
  // we could try to do it using the material-ui onOpen callback
  // so that choices are fetched only when the dropdown is opened/interacted with
  React.useEffect(
    () => {
      setChoices(
        getResponse('get_content', {resource: 'dir', value: source})
      );
    },
    [source]
  );

  const param = useContext(BuildParamsContext)[paramKey];
}

function SingleFileSelectorWithCtx({ paramKey }) {
  const params= useContext(BuildParamsContext);
  const dispatch = useContext(BuildParamsDispatchContext);

  const param = params[paramKey];

  const handleChange = (e) => {
    dispatch(setBuildParamValue(paramKey, e.target.value));
  };

  return (
    <FormControl>
      <Select
        variant="outlined"
        value={param.value}
        onChange={handleChange}
        renderValue={(item) => (<MenuItem key={item} value={item}>{item}</MenuItem>)}
      >
        {param.choices}
      </Select>
      <FormHelperText>{param.description}</FormHelperText>
    </FormControl>
  )
}

function SelectFileStageWithCtx({ stage }) {
  return (
    <>
      <SingleFileSelectorWithCtx paramKey="file.A" />
      <SingleFileSelectorWithCtx paramKey="file.B" />
    </>
  );
}

function SingleFileSelectorWithHook({paramKey}) {
  const buildState = useContext()
  const useBuildParam = (k) => { return ['foo', (v) => v, {}]; };
  const [value, setValue, param] = useBuildParam(paramKey);

  return (
    <Select
      value={value}
    >
    </Select>
  )
}

function SelectFileStage({ stage, dispatch }) {
  const getSelector = (param) => {
    return (
      <SingleFileSelector
        paramKey={param.key}
        value={param.value}
        compareSide={param.compareSide}
        source={param.source}
        dispatch={dispatch}
      />
    )
  };
  return (
    <>
      {stage.buildParams.map(getSelector)}
    </>
  )
}

// TODO this should be called "FITSStage" (or "fits.SelectHDUStage")
function FITSSelector({ stage, dispatch }) {
  let columnDefs = [
    { title: 'No', field: 'extension' },
    { title: 'Name', field: 'name' },
    { title: 'HDU Type', field: 'hdu_type' },
    { title: 'Dimensions', field: 'dimensions' },
    { title: 'Content Type', field: 'content_type' }
  ];

  const getDescription = (side) => {
    return `Choose HDU (${side}) (from ${stage.source[side]})`;
  };

  return (
    <div>
      <TableSelector
        name="fits.hdu.A"
        description={getDescription("A")}
        choices={stage.choices.A}
        columns={columnDefs}
        dispatch={dispatch}
      />
      <TableSelector
        name="fits.hdu.B"
        description={getDescription("B")}
        choices={stage.choices.B}
        columns={columnDefs}
        dispatch={dispatch}
      />
    </div>
  )
}

function SelectAnalysisParams({ stage, dispatch }) {

  return (
    <div>
      <FormGroup column>
        <BoolSelector
          name={'analysisParams.normalize'}
          description="Normalize arrays?"
          value={true}
          dispatch={dispatch}
        />
        <ChoiceSelector
          name={'analysisParams.visualization'}
          description="Visualization type"
          choices={['heatmap', 'histogram']}
          dispatch={dispatch}
        />
      </FormGroup>
    </div>
  )
}


function TextSelector({ description, setSelectedValue }) {
  return (
    <TextField
      // id={`${res}-${stage.action}-A`}
      label={description}
      helperText={description}
      variant="outlined"
      onChange={e => setSelectedValue(e.target.value)}
    />
  )
}

function BoolSelector({ name, description, value, dispatch }) {
  const [selected, setSelected] = useState(value);
  const handleChange = (e) => {
    let val = e.target.checked;
    setSelected(val);
    dispatch({ type: 'setFormData', name: name, value: val });
  }
  return (
    <FormControlLabel
      control={
        <Checkbox
          // TODO think if we need/want to pass the initial value as well
          checked={selected}
          onChange={handleChange}
        // inputRef={inputRef}
        // defaultChecked={inputRef.current.checked}
        />
      }
      label={description}
    />
  )
}

function ChoiceSelector({ name, description, choices, dispatch }) {

  // console.log(`ChoiceSelector.props=`); console.log(props)
  // console.log(`ChoiceSelector.description=`); console.log(description)
  // console.log(`ChoiceSelector.setSelectedValue=`); console.log(setSelectedValue)
  function renderChoice(item, index) {
    return (
      <MenuItem key={index} value={item}>{item}</MenuItem>
    );
  };

  // make sure that the first choice is always a placeholder value
  choices = ['---', ...choices];

  const [selected, setSelected] = useState(choices[0]);
  const handleChange = (e) => {
    let val = e.target.value;
    setSelected(val);
    dispatch({ type: 'setFormData', name: name, value: val });
  }

  return (
    // <FormControl className={classes.formControl}>
    <FormControl>
      <Select
        variant="outlined"
        //   TODO decide if this needs to be preselected or not
        value={selected}
        onChange={handleChange}
      //   defaultValue={props.choices[0]}
      //   inputRef={inputRef}
      >
        {choices.map(renderChoice)}
      </Select>
      <FormHelperText>{description}</FormHelperText>
    </FormControl>
  )
}

function FixedSelector({ name, description, value, dispatch }) {
  return (
    <Typography>
      <code>
        {value}
      </code>
    </Typography>
  )
}

function TableSelector({ name, description, choices, dispatch, ...props }) {

  const handleChange = (rows) => {
    let singleRow = rows[0];
    dispatch({ type: 'setFormData', name: name, value: { ...singleRow } });
  }

  return (
    <MaterialTable
      columns={props.columns}
      title={description}
      data={choices}
      options={{
        selection: true
      }}
      // TODO also somehow force the fact that only a single entry should be selected
      // for the moment, we can fall back on always returning the first selected row
      onSelectionChange={handleChange}
    />
  )
}


export {
  ComparisonBuilder,
}
