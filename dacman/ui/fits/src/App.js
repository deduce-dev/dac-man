import React from 'react';
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
} from './Layout'

import {
  getActiveComparisons
} from './api'

import MainMetaBuilder from './MainMetaBuilder';
import Summary from './Summary'
import Compare from './Compare'


function ShowMain() {
  return (
    <MainLayout>
      <Sidebar cardContentItems={getActiveComparisons()}/>
    </MainLayout>
  )
}

function ShowCompare() {
  return (
    <MainLayout>
      <Compare />
      <Sidebar cardContentItems={getActiveComparisons()}/>
    </MainLayout>
  )
}

function ShowSummary() {
  return (
    <MainLayout>
      <Summary />
      <Sidebar cardContentItems={getActiveComparisons()}/>
    </MainLayout>
  )
}

class App extends React.Component {

  render() {
    return (
      <Router>
        <div className="App">
          <Switch>
            <Route exact path="/" component={ShowMain} />
            {/* TODO "/meta" will not work as-is */}
            <Route path="/meta" component={MainMetaBuilder} />
            <Route path="/compare" component={ShowCompare} />
            <Route path="/summary" component={ShowSummary} />
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App;
