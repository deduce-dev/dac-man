import React from 'react';
import MainMetaBuilder from './MainMetaBuilder.jsx';
import Summary from './Summary.jsx'
import {
  HashRouter as Router,
  Switch,
  Route,
  Link,
  useRouteMatch,
  useParams
} from "react-router-dom";
import logo from './logo.svg';
import deducelogo from './deducelogo.png';
import './App.css';


class HeaderBar extends React.Component {
  render() {
    return (
      <div class="header">
        <div class="flex-container logo">
          <div><img src={deducelogo} alt=""/></div>
          <div class="logo-text">Deduce</div>
        </div>
        <div class="flex-right rightnav">About</div>
        <div class="rightnav">Documentation</div>
      </div>
    );
  }
}




class App extends React.Component {

  render() {
    return (
      <Router>
        <div className="App">
          <HeaderBar />
           <Switch>
            <Route path="/meta">
              <MainMetaBuilder />
            </Route>
            <Route path="/">
              <Summary />
            </Route>
          </Switch>
        </div>
      </Router>
    );
  }
}

export default App;
