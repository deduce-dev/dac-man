import React from 'react';
import logo from './logo.svg';
import deducelogo from './deducelogo.png';
import './App.css';

console.log("logo is");
console.log(deducelogo);


class MainContent extends React.Component {
  render() {
    return (
      <div class="maincontent flex-body">
          <SideBar />
          <MetaBuilder /> 
      </div>
    );
  }
}

class SideBar extends React.Component {
  render() {
    return (
      <div class="sidebar flex-sidebar">sidebar test2 </div>
    );
  }
}

class MetaBuilder extends React.Component {
  render() {
    return (
      <div class="metabuilder flex-content">meta test </div>
    );
  }
}


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



function App() {
  return (
    <div className="App">
      <HeaderBar />
      <MainContent />

    </div>
  );
}

export default App;
