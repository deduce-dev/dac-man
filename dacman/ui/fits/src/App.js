import React, { useState, useReducer } from "react";
import TextField from '@material-ui/core/TextField';
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
  useRouteMatch,
  useParams
} from "react-router-dom";
import logo from './logo.svg';
import deducelogo from './deducelogo.png';
import './App.css';
import Button from '@material-ui/core/Button'
import AppBar from '@material-ui/core/AppBar'
import Toolbar from '@material-ui/core/Toolbar'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles';
import Paper from '@material-ui/core/Paper'

import {
  MainLayout,
  Sidebar,
  SimplerWorkbench,
  WorkbenchWithReducer,
  SimplerSidebar
} from './Layout'

import {
  getComparisonGeneric,
  getComparisons,
  buildComparisonReducer,
  initBuildState,
  comparisonsReducer,
  BuildContextProvider,
  getComparisonHDF5,
} from './api'

import {
  ComparisonBuilder
} from './Workbench'

import {
  WorkbenchContainer,
  SlimComparisonBuilder,
  StagesContextProvider,
  ParamsContextProvider,
} from './build';

import MainMetaBuilder from './MainMetaBuilder';
import Summary from './Summary'
import Compare from './Compare'


function ShowMain(comparisons) {
  return (
    <MainLayout>
      <Sidebar cardContentItems={comparisons}/>
    </MainLayout>
  )
}

function ShowCompare(comparisons, cid) {
  // let cid = useParams();
  // let cid = parseInt(useParams().cid);
  // let cid = parseInt(cid);
  let comparison = comparisons.find(c => c.comparisonID === parseInt(cid));
  return (
    <MainLayout>
      <Compare comparison={comparison}/>
      <Sidebar cardContentItems={comparisons}/>
    </MainLayout>
  )
}

function ShowCompareNew(comparisons) {
  let newID = comparisons.length + 1;
  let newComparison = getComparisonGeneric(newID, "dat", [`final-v${newID}`, `final-v${newID}-FINAL`]);
  comparisons.push(newComparison);
  return (
    <MainLayout>
      <Compare comparison={newComparison}/>
      <Sidebar cardContentItems={comparisons}/>
    </MainLayout>
  )
}

function ShowSummary(comparisons, cid) {
  let comparison = comparisons.find(c => c.comparisonID === parseInt(cid)) || getComparisonHDF5();
  let demoComparisonOldSchema = getComparisonHDF5();
  comparison.results = comparison.results || demoComparisonOldSchema.results;

  return (
    <MainLayout>
      <Summary comparison={comparison}/>
      {/* <Sidebar cardContentItems={comparisons}/> */}
    </MainLayout>
  )
}

// WHY this intermediate component seems to be necessary to avoid the "invalid hook call" error
// my guess is that it could be related to the fact that we're calling it through the react-router `render` prop
function ShowWorkbench() {

  return (
    // <WorkbenchArea />
    <CreateComparisonView />
  );
}

function WorkbenchArea() {
  const [comparisons, setComparisons] = useState([]);
  const [nextCid, setNextCid] = useState(0);

  function createComparison(workbenchData) {
    console.log('createComparison.workbenchData'); console.log(workbenchData);
    const cid = nextCid;
    setNextCid(cid + 1);
    return {
      comparisonID: cid,
      ...workbenchData
    }
  }

  function addComparison(workbenchData) {
    console.log('addComparison.workbenchData'); console.log(workbenchData);
      setComparisons([...comparisons, createComparison(workbenchData)]);
  };

  return (
    <MainLayout>
      <WorkbenchWithReducer runAction={addComparison}/>
      <SimplerSidebar comparisons={comparisons}/>
    </MainLayout>
  );
}

function CreateComparisonView() {
  const [comparisons, dispatch] = useReducer(comparisonsReducer, []);
  // const [comparisonWIP, dispatchBuild] = useReducer(buildComparisonReducer, null, getNewComparisonBuildState);
  const [comparisonWIP, dispatchBuild] = useReducer(
    buildComparisonReducer,
    (formData) => {dispatch({type: 'addFromBuild', buildData: formData})},
    initBuildState
  );
  // const [comparisonWIP, dispatch] = useState({});
  return (
    <MainLayout>
      <BuildContextProvider>
        <ComparisonBuilder
        state={comparisonWIP}
        dispatch={dispatchBuild} 
        />
      </BuildContextProvider>
      <SimplerSidebar
        comparisons={comparisons}
        comparisonWIP={comparisonWIP}
      />
    </MainLayout>
  )
}

function ShowBuildWorkbench() {
  return <BuildComparisonView />
}

function BuildComparisonView(props) {
  return (
    <MainLayout>
      <ParamsContextProvider>
        <WorkbenchContainer>
          <StagesContextProvider>
            <SlimComparisonBuilder />
          </StagesContextProvider>
        </WorkbenchContainer>
      </ParamsContextProvider>
    </MainLayout>
  );
}

class App extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      comparisons: getComparisons()
    };
  }

  // componentDidMount() {
  //   this.state.comparisons = getComparisons();
  // }

  render() {
    return (
      <Router>
        <div className="App">
          <Switch>
            {/* <Route exact path="/" component={ShowMain} /> */}
            {/* TODO "/meta" will not work as-is */}
            {/* <Route path="/meta" component={MainMetaBuilder} />
            <Route path="/:cid/compare" component={ShowCompare} />
            <Route path="/:cid/summary" component={ShowSummary} /> */}
            {/* <Route Route exact path="/" render={(routeProps) => ShowMain(this.state.comparisons)} /> */}
            <Route Route exact path="/" render={(routeProps) => ShowWorkbench()} />
            <Route Route exact path="/compare" render={(routeProps) => ShowCompareNew(this.state.comparisons)} />
            <Route path="/:cid/compare" render={(routeProps) => ShowCompare(this.state.comparisons, routeProps.match.params.cid)} />
            <Route path="/:cid/summary" render={(routeProps) => ShowSummary(this.state.comparisons, routeProps.match.params.cid)} />
            <Route path="/workbench" render={(routeProps) => ShowWorkbench()} />
            <Route path="/build" render={(routeProps) => ShowBuildWorkbench()} />
            {/* <Route path="/workbench" render={(routeProps) => CreateComparisonView()} /> */}
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App;
