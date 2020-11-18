import React, { useState, useRef } from "react";
import { makeStyles } from "@material-ui/core/styles";
import Drawer from "@material-ui/core/Drawer";
import AppBar from "@material-ui/core/AppBar";
import CssBaseline from "@material-ui/core/CssBaseline";
import Toolbar from "@material-ui/core/Toolbar";
import List from "@material-ui/core/List";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import {Tab, Tabs} from "@material-ui/core";

import { Paper, Container, Grid, Card, Box } from "@material-ui/core";
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

import { Link as RouterLink, useParams } from "react-router-dom";
import { getLayer, getComparisonGeneric } from "./api"

import { SubmitSelected, ChoiceSelector, BoolSelector, TableSelector, FixedSelector } from "./Selectors"

const drawerWidth = 480;

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex"
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
    padding: theme.spacing(2),
    backgroundColor: '#c5c5c5',
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3)
  },
  toolbar: theme.mixins.toolbar,
  paper: {
    padding: theme.spacing(2),
    display: "flex",
    overflow: "auto",
    flexDirection: "column"
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4)
  },
  sidebarContent: {
    // padding: theme.spacing(3),
  },
  appBarToolbar: {
    display: "flex", flexGrow: 1, justifyContent: "space-between"
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 480,
  },
  paddedFormControl: {
    padding: theme.spacing(2),
  },
}));

function WorkbenchCard({ children, title }) {
  const classes = useStyles(); 
  return (
    <Grid item xs={12}>
      <Paper elevation={5} className={classes.paper}>
        <Typography variant="h6">
          {title}
        </Typography>
        {children}
      </Paper>
      {/* <Button variant="contained" color="primary" onClick={()=>console.log('This was clicked!')}>Do something</Button> */}
    </Grid>
  );
}

function SidebarCard({comparison: cmp}) {
  const classes = useStyles();
  // let { cid } = useParams();
  console.log(cmp);
  let cid = cmp.comparisonID;
  // let layer = getLayer(cmp, "file")
  return (
    <Paper elevation={5} className={classes.paper}>
      <div>
      <Typography variant="h6">
          Comparison ID: {cid}
        </Typography>
        <Typography variant="h6">
          {cmp.data.file.A} -> {cmp.data.file.A}
        </Typography>
        <Button color="primary" component={RouterLink} to={`/${cid}/compare`}>Edit</Button>
        <Button color="primary" component={RouterLink} to={`/${cid}/summary`}>Summary</Button>
      </div>
    </Paper>
  );
}

function Sidebar({cardContentItems = []}) {
    const classes = useStyles();
    const renderItem = (item, index) => {
      console.log(item)
        return (
          <Grid key={item.comparisonID} item xs={12}>
            <SidebarCard comparison={item}/>
          </Grid>
        );
    }
    return (
        <Drawer
            className={classes.drawer}
            variant="permanent"
            anchor="right"
            classes={{
            paper: classes.drawerPaper,
            }}
        >
            <div className={classes.toolbar} />
            
            <Box display="flex" justifyContent="space-between">
              <Typography variant="h4">History</Typography>
              <Button variant="contained" color="primary" component={RouterLink} to={`/compare`}>
                Add comparison
              </Button>
            </Box>
            <Grid container className={classes.sidebarContent} spacing={2}>
              <Grid item xs={12}>
              </Grid>
              {cardContentItems.map(renderItem)}
            </Grid>
        </Drawer>
    );
}

function BuildComparisonSidebarCard({buildData}) {
    const classes = useStyles();

    return (
      <Grid key="build-comparison" item xs={12}>
        <Paper elevation={5} className={classes.paper}>
          <div>
            <Typography variant="h6">
              Comparison parameters:
            </Typography>
            <PrettyPrinter item={buildData.formData} />
            {/* <Button color="primary" component={RouterLink} to={`/${cid}/compare`}>Edit</Button>
            <Button color="primary" component={RouterLink} to={`/${cid}/summary`}>Summary</Button> */}
          </div>
        </Paper>
      </Grid>
    );
}

function SimplerSidebar({comparisons, comparisonWIP}) {
  const classes = useStyles();

  function renderComparison(comparison, index) {
    const cid = index;
    return (
      <Grid key={cid} item xs={12}>
        <Paper elevation={5} className={classes.paper}>
          <div>
            <Typography variant="h6">
              Comparison ID: {cid}
            </Typography>
            {/* <PrettyPrinter item={comparison} /> */}
            <Typography variant="h6">
              {comparison.data.file.A} -> {comparison.data.file.B}
            </Typography>
            {/* <Typography variant="h6">
              {comparison.path.A} -> {comparison.path.B}
            </Typography> */}
            <Button color="primary" component={RouterLink} to={`/${cid}/compare`}>Edit</Button>
            <Button color="primary" component={RouterLink} to={`/${cid}/summary`}>Summary</Button>
          </div>
        </Paper>
      </Grid>
    );
  };

  return (
    <Drawer
      className={classes.drawer}
      variant="permanent"
      anchor="right"
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <div className={classes.toolbar} />
      <Box display="flex" justifyContent="space-between">
        <Typography variant="h4">History</Typography>
        <Button color="primary" component={RouterLink} to={`/workbench`}>
          New comparison
        </Button>
      </Box>
      <Grid container className={classes.sidebarContent} spacing={2}>
        <Grid item xs={12}></Grid>
        {comparisons.map(renderComparison)}
        <BuildComparisonSidebarCard buildData={comparisonWIP} />
      </Grid>
    </Drawer>
  );
}

function getTitleForLayer(item) {
  const capitalizeFirst = (str) => str.charAt(0).toUpperCase() + str.slice(1);
  let title = item.title || capitalizeFirst(item.type);
  return title;
}

export function PrettyPrinter({item}) {
  return (
    <div>
      <code>
        <pre>
          {JSON.stringify(item, null, '  ')}
        </pre>
      </code>
    </div>
  )
}

function SelectAnalysisParams({stage, dispatch, classes}) {
  // const [data, setData] = useState({
  //   normalize: true,
  //   visualization: ''
  // });
  // const normalizeRef = useRef(true);
  // const visualizationRef = useRef('---');

  // const [normalize, setNormalize] = useState(true);
  // const visualizationChoices = ['---', 'heatmap', 'histogram'];
  // const [visualization, setVisualization] = useState(visualizationChoices[0]);

  return (
    <div>
      <FormGroup column>
        <BoolSelector
          name={'analysisParams.normalize'}
          description="Normalize arrays?"
          // inputRef={normalizeRef}
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

function GenericSelector({stage, dispatch, classes, resource = 'resource'}) {
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


function FileSelector({stage, dispatch, classes}) {
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


function FITSSelector({stage, dispatch, classes}) {
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

function DirSelector({stage, dispatch, classes}) {
  return (
    <>
      <FixedSelector
        name="dir.A"
        value="/data/solar-system-v1/"
        dispatch={dispatch}
      />
      <br/>
      <FixedSelector
        name="dir.B"
        value="/data/solar-system-v2/"
        dispatch={dispatch}
      />
    </>
  )
}

// this simulates an actual call to the backend
function getResponse(action, params) {
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
        source: {...src}
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
        description: "Select the two HDUs to compare",
        choices: {
          A: resp.A.values,
          B: resp.B.values,
        },
        source: {...src}
      };
    }
    else {
      next = {
        action: "set_parameters",
        resource: "analysis_params",
        description: "Select the analysis parameters",
        isLast: true
      };
    };

    return next;
}

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

function NextControls({stage, dispatch}) {
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


function stageBuildReducer(state, action) {
  console.log('inside stageBuildReducer');
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
      return {
        ...state,
        stages: [getNextStage()]
      };
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
      return {
        ...state
      };
  default:
    return state;
  };
}


function WorkbenchWithReducer({runAction}) {
  const classes = useStyles();
  const initialState = {
    stages: [getNextStage()],
    formData: {
      "dir.A": "/data/solar-system-v1/",
      "dir.B": "/data/solar-system-v2/",
    },
    onFormDataComplete: runAction,
  };
  const [state, dispatch] = React.useReducer(stageBuildReducer, initialState); 

  function getWorkbenchCard(stage, index) {
    // this variable must be capitalized, or the component will not be treated correctly!
    // see also https://reactjs.org/docs/jsx-in-depth.html#choosing-the-type-at-runtime
    const StageComponent = getComponent(stage);
    // const NextControls = getNextControls(stage, dispatch);
    // console.log('getWorkbenchCard.component:'); console.log(component);
    return (
      <>
        <WorkbenchCard
          key={`card-${index}`}
          title={`Step #${index}`}
          classes={classes}
        >
          <Typography>{stage.description}</Typography>
          <StageComponent key={index} stage={stage} dispatch={dispatch} classes={classes} />
        </WorkbenchCard>
      </>
    );
  };

  const InitialComponent = () => {
    return (
      <WorkbenchCard
        key="card-initial"
        title="Dirs under comparison"
        classes={classes}
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
        <Button variant="contained" color="primary" onClick={e => dispatch({type: 'resetStages'})}>Reset</Button>
        <Grid container spacing={3}>
          {state.stages.map(getWorkbenchCard)}
        </Grid>
        {state.stages.slice(-1).map(stage => <NextControls stage={stage} dispatch={dispatch} />)}
      </Container>
    </main>
  );
}


function SimplerWorkbench({runAction}) {
    const classes = useStyles();
    const initialStage = getNextStage();
    const initialComponent = getComponent(initialStage);
    const [stages, setStages] = useState([initialStage]);
    const [components, setComponents] = useState([initialComponent]);
    
    function addStage() {
      const toCheck = stages.slice(-1)[0];
      const toBeAdded = getNextStage(toCheck);
      console.log('addStage.stages:'); console.log(stages);
      console.log('addStage.toCheck:'); console.log(toCheck);
      setStages([...stages, toBeAdded]);
      setComponents([...components, getComponent(toBeAdded)]);
    };
    
    function resetStages() {
      setStages([getNextStage()]);
    }

    const [formData, setFormData] = useState([]);

    function storeDataForStage(data) {
      setFormData([...formData, data]);
      addStage();
    }

    function getWorkbenchCard(stage, index) {
      // this variable must be capitalized, or the component will not be treated correctly!
      // see also https://reactjs.org/docs/jsx-in-depth.html#choosing-the-type-at-runtime
      const StageComponent = components[index];
      // console.log('getWorkbenchCard.component:'); console.log(component);
      return (
        <WorkbenchCard
          key={`card-${index}`}
          title={`Step #${index}`}
          classes={classes}
        >
          <Typography>{stage.description}</Typography>
          <StageComponent key={index} stage={stage} dispatchFormData={storeDataForStage} classes={classes} />
          {/* <FileSelector stage={item} classes={classes} /> */}
          {/* <SimpleWorkbenchComponent stage={item} action={e => addStage()} classes={classes}/> */}
        </WorkbenchCard>
      );
    };

    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        <Container maxWidth="lg" className={classes.container}>
          <WorkbenchCard
           title="dirs under comparison"
           classes={classes}
          >
            <Typography>
              /data/solar-system-v1, /data/solar-system-v2 
            </Typography>
          </WorkbenchCard>
          <Typography variant="h4">{`Number of stages: ${stages.length}`}</Typography>
          <Button variant="contained" color="primary" onClick={e => resetStages()}>Reset</Button>
          <Grid container spacing={3}>
            {stages.map(getWorkbenchCard)}
          </Grid>
        <Button variant="contained" color="primary" onClick={e => runAction({formData: formData})}>Run</Button>
        </Container>
      </main>
    );
}

function Workbench({items = [], getComponent, getTitle = getTitleForLayer}) {
    const classes = useStyles();
    let { cid } = useParams();
    const getWorkbenchCard = (item, index) => {
      // let component = getComponent(item) || PrettyPrinter;
      let component = getComponent(item);
      if (!component) return;
      let title = getTitle(item);
      return (
        <WorkbenchCard
          key={index}
          title={title}
          classes={classes}
        >
          {component && component({...item, classes: classes})}
        </WorkbenchCard>
      );
    };

    return (
      <main className={classes.content}>
        <div className={classes.toolbar} />
        <Container maxWidth="lg" className={classes.container}>
          <Typography variant="h4">{`Comparison ID: ${cid}`}</Typography>
          <Grid container spacing={3}>
            {items.map(getWorkbenchCard).filter(Boolean)}
          </Grid>
        </Container>
      </main>
    );
}

function MainLayout(props) {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar position="fixed" className={classes.appBar}>
        <Toolbar className={classes.appBarToolbar}>
          {/* <Typography flexGrow={1} variant="h6"> */}
          <Box>
            <Typography variant="h6">
              Deduce
            </Typography>
          </Box>
          <Box>
            <Button color="inherit">About</Button>
            <Button color="inherit">Documentation</Button>
          </Box>
        </Toolbar>
      </AppBar>
      {props.children}
    </div>
  );
}

export {
  MainLayout,
  WorkbenchWithReducer,
  Workbench,
  SimplerWorkbench,
  Sidebar,
  SimplerSidebar,
  useStyles,
  WorkbenchCard,
}
