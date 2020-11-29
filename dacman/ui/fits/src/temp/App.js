import React, { useReducer } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

import logo from '../logo.svg';
import deducelogo from '../deducelogo.png';
import './App.css';

import { getComparisons } from '../common/api'
import { MainLayout } from '../components/Layout'
import { FileUploader } from '../components/FileUploader'


// WHY this intermediate component seems to be necessary to avoid the "invalid hook call" error
// my guess is that it could be related to the fact that we're calling it through the react-router `render` prop
function ShowFlagWorkbench() {
  return (
    <CreateFlaggingView />
  );
}

function CreateFlaggingView() {
  //const [state, dispatch] = useReducer(flaggingReducer, {});

  return (
    <MainLayout>
      <FileUploader />
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

  render() {
    return (
      <Router>
        <div className="App">
          <Switch>
            {/* <Route Route exact path="/" render={(routeProps) => ShowWorkbench()} /> */}
            <Route path="/flag" render={(routeProps) => ShowFlagWorkbench()} />
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App;
