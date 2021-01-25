import React, { useReducer } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

import './App.css';

import { FlaggingView } from './components/FlaggingView';
import { DatadiffView } from "./components/DatadiffView";


// WHY this intermediate component seems to be necessary to avoid the "invalid hook call" error
// my guess is that it could be related to the fact that we're calling it through the react-router `render` prop
function ShowFlagWorkbench() {
  return (
    <FlaggingView />
  );
}

function ShowDatadiffWorkbench() {
  return (
    <DatadiffView />
  );
}

class App extends React.Component {

  render() {
    return (
      <Router>
        <div className="App">
          <Switch>
            {/* <Route Route exact path="/" render={(routeProps) => ShowWorkbench()} /> */}
            <Route path="/flag" render={(routeProps) => ShowFlagWorkbench()} />
            <Route path="/datadiff" render={(routeProps) => ShowDatadiffWorkbench()} />
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App;
