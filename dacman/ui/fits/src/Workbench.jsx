import React, { useState, useContext } from 'react';

import {
  Container,
  Grid,
  Card,
  Typography
} from "@material-ui/core";
import Button from "@material-ui/core/Button";
import Input from '@material-ui/core/Input';
import InputAdornment from '@material-ui/core/InputAdornment';
import TextField from "@material-ui/core/TextField";
import MenuItem from "@material-ui/core/MenuItem";
import Select from "@material-ui/core/Select";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormGroup from "@material-ui/core/FormGroup";
import Checkbox from "@material-ui/core/Checkbox";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';

import MaterialTable from 'material-table';

import CloudUploadIcon from '@material-ui/icons/CloudUpload';

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

function FileUploader({ stage, dispatch }) {
  const classes = useStyles();

  function createData(datetime, WindDir, Windspeed_ms, temp_f, dewp_f) {
    return { datetime, WindDir, Windspeed_ms, temp_f, dewp_f };
  }

  const rows = [
    createData('1/3/08 0:00', 330, 3.576, 81, 68),
    createData('1/3/08 1:00', 340, 1.341, 79, 68),
    createData('1/3/08 2:00', 'NA', 'NA', 'NA', 'NA'),
    createData('1/3/08 3:00', 'NA', 'NA', 'NA', 'NA'),
    createData('1/3/08 4:00', 'NA', 'NA', 'NA', 'NA'),
  ];

  return (
    <main className={classes.content}>
      <div className={classes.toolbar} />
      <Container maxWidth="lg" className={classes.container}>
        <Grid container spacing={3}>
          <WorkbenchCard
            key="card-initial"
            title="Choose File for flagging"
          >
            <TextField
              disabled
              fullWidth
              id="standard-disabled"
              defaultValue="4_NGEE/Powell/PNM_WS/AirportData_2008-2019_v3.csv"
              className={classes.textField}
              margin="normal"
            />
            <input
              accept="*.csv"
              className={classes.input}
              style={{ display: 'none' }}
              id="raised-button-file"
              type="file"
            />
            <br />
            <label htmlFor="raised-button-file">
              <Button
                variant="raised"
                component="span"
                className={classes.button}
                startIcon={<CloudUploadIcon />}
              >
                Upload File
              </Button>
            </label>
          </WorkbenchCard>
          <WorkbenchCard
            key="card-1"
            title="Preview"
          >
            <Table className={classes.table} aria-label="simple table">
              <TableHead>
                <TableRow>
                  <TableCell style={{ fontWeight: 'bold' }}>datetime</TableCell>
                  <TableCell align="right" style={{ fontWeight: 'bold' }}>WindDir</TableCell>
                  <TableCell align="right" style={{ fontWeight: 'bold' }}>Windspeed_ms</TableCell>
                  <TableCell align="right" style={{ fontWeight: 'bold' }}>TEMP_F</TableCell>
                  <TableCell align="right" style={{ fontWeight: 'bold' }}>DEWP_F</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.datetime}>
                    <TableCell component="th" scope="row">
                      {row.datetime}
                    </TableCell>
                    <TableCell align="right">{row.WindDir}</TableCell>
                    <TableCell align="right">{row.Windspeed_ms}</TableCell>
                    <TableCell align="right">{row.temp_f}</TableCell>
                    <TableCell align="right">{row.dewp_f}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Button
              variant="contained"
              color="primary"
            >
              Next
            </Button>
          </WorkbenchCard>
          <WorkbenchCard
            key="card-2"
          >
            <CSVVariableSelector />
            <Button
              variant="contained"
              color="primary"
            >
              Next
            </Button>
          </WorkbenchCard>
          <WorkbenchCard
            key="card-3"
            title="TEMP_F"
          >
            <VariableFlaggingDetails dispatch={dispatch} />
            <Button
              variant="contained"
              color="primary"
            >
              Next
            </Button>
          </WorkbenchCard>
          <WorkbenchCard
            key="card-4"
            title="Review Flagging Steps"
          >
            <Typography variant="h7" gutterBottom>
              Checking Null values for:
            </Typography>
            <Typography variant="h7" className={classes.paddedFormControl} gutterBottom>
              - TEMP_F
            </Typography>
            <Typography variant="h7" gutterBottom>
              Checking Duplicate values for:
            </Typography>
            <Typography variant="h7" className={classes.paddedFormControl} gutterBottom>
              - TEMP_F
            </Typography>
            <Button
              variant="contained"
              color="primary"
            >
              Run
            </Button>
          </WorkbenchCard>
        </Grid>
      </Container>
    </main>
  )
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

function CSVVariableSelector({ stage, dispatch }) {
  let columnDefs = [
    { title: 'Variables', field: 'variable_name' },
    { title: 'Dimensions', field: 'dimensions' },
    { title: 'Content Type', field: 'content_type' }
  ];

  let values= [
    {
        variable_name: 'datetime',
        dimensions: '(1, 105192)',
        content_type: 'String'
    },
    {
        variable_name: 'WindDir',
        dimensions: '(1, 105192)',
        content_type: 'Integer'
    },
    {
        variable_name: 'Windspeed_ms',
        dimensions: '(1, 105192)',
        content_type: 'Float'
    },
    {
        variable_name: 'TEMP_F',
        dimensions: '(1, 105192)',
        content_type: 'Integer'
    },
    {
        variable_name: 'DEWP_F',
        dimensions: '(1, 105192)',
        content_type: 'Integer'
    },
  ]

  return (
    <MaterialTable
      columns={columnDefs}
      title="Choose Variables to flag"
      data={values}
      options={{
        selection: true
      }}
    />
  )
}

function VariableFlaggingDetails({ stage, dispatch }) {
  const classes = useStyles();

  const [state, setState] = React.useState({
    checkedA: true,
    checkedB: true,
    checkedC: false,
    checkedD: false,
    checkedE: false,
  });

  const handleChange = (event) => {
    setState({ ...state, [event.target.name]: event.target.checked });
  };

  const handleValueChange = (prop) => (event) => {
    setState({ ...state, [prop]: event.target.value });
  };

  return (
    <FormControl component="fieldset" className={classes.formControl}>
      <FormGroup>
        <FormControlLabel
          control={<Checkbox checked={state.checkedA} onChange={handleChange} name="checkedA" />}
          label="Check Null values"
        />
        <FormControlLabel
          control={<Checkbox checked={state.checkedB} onChange={handleChange} name="checkedB" />}
          label="Check Duplicate values"
        />
        <FormGroup row className={classes.paddedFormControl}>
          <FormControlLabel
            control={<Checkbox checked={state.checkedC} onChange={handleChange} name="checkedC" />}
            label="Find subsequent Duplicates"
          />
          <FormControl>
            <TextField
              id="subsequent_duplicates_n"
              value={3}
              InputProps={{
                startAdornment: <InputAdornment position="start">n =</InputAdornment>,
              }}
            />
          </FormControl>
        </FormGroup>
        <FormControlLabel
          control={<Checkbox checked={state.checkedD} onChange={handleChange} name="checkedD" />}
          label="Check Bad values"
        />
        <FormGroup row className={classes.paddedFormControl}>
          <FormControl>
            <TextField
              id="iqr_coef"
              InputProps={{
                startAdornment: <InputAdornment position="start">Range</InputAdornment>,
              }}
            />
            <TextField
              id="iqr_coef"
              InputProps={{
                startAdornment: <InputAdornment position="start">To</InputAdornment>,
              }}
            />
          </FormControl>
        </FormGroup>
        <FormControlLabel
          control={<Checkbox checked={state.checkedE} onChange={handleChange} name="checkedE" />}
          label="Check Outlier values"
        />
        <FormGroup row className={classes.paddedFormControl}>
          <FormControl>
            <TextField
              id="iqr_coef"
              value={1.5}
              InputProps={{
                startAdornment: <InputAdornment position="start">IQR Coefficient =</InputAdornment>,
              }}
            />
          </FormControl>
        </FormGroup>
      </FormGroup>
    </FormControl>
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
  FileUploader,
}
