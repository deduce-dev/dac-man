import React from 'react';
import logo from './logo.svg';
import deducelogo from './deducelogo.png';
import './App.css';


class FileType extends React.Component {
  render() {
    return (
      <div class="card column">
        <div class="input-group">
          <label>File Format for Comparison</label>
          <select id="file_format">
            <option value="" selected="selected"></option>
            <option value="office" >fits</option>
            <option value="town_hall" >csv</option>
          </select>
        </div>
      </div>
    );
  }
}

class DataModelInfo extends React.Component {
  render() {
    return (
      <div class="card column">
        <div class="card-title">Data Model Information</div>
        <div class="card-subsection">
          <div class="input-group">
            <label>Select Example File</label>
            <input type="text" />
          </div>
        </div>
        <div>
          <div class="table-prompt">Which HDU's do you want to compare?</div>
          <table>
            <thead> 
              <tr>
                <th>&nbsp;</th>
                <th>No</th>
                <th>Name</th>
                <th>HDU Type</th>
                <th>Dimension</th>
                <th>Content Type</th>
              </tr>
            </thead>
            <tbody>
              <tr>
                <td><input type="checkbox"/></td>
                <td>1</td>
                <td>PRIMARY</td>
                <td>image</td>
                <td>(4200,1000)</td>
                <td><input type="text" /></td>
              </tr>
            </tbody>
          </table>
        </div>

      </div>
    );
  }
}

class VisInfo extends React.Component {
  render() {
    return (
      <div class="card column">
        <div class="card-title">Visualization Information</div>
        <div>
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>Comparison Type</th>
                <th>Visualization Type</th>
             </tr>
            </thead>
            <tbody>
              <tr>
                <td>PRIMARY</td>
                <td><input type="text" /></td>
                <td><input type="text" /></td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    );
  }
}

class ComparingFiles extends React.Component {
  render() {
    return (
      <div class="card column">
        <div class="card-title">Comparing Files</div>
        <div class="radio-group">
          <input type="radio" />
          <label>Comparing 2 Files</label>
          <input type="radio" />
          <label>Comparing Multiple Files/Directories</label>
        </div>
        <div class="input-group">
          <label>Compare Files</label>
          <input type="text" />
        </div>
      </div>
    );
  }
}

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
      <div class="sidebar flex-sidebar"> 
        <div class="column">
          <div class="return">
            <i className='material-icons' style={{fontSize: '18px', width: '30px', verticalAlign: 'middle'}}>arrow_back_ios</i>Return to Overview
          </div>
          <div class="comparators">
            <div class="comparator-section-title">Custom Comparators</div>
          </div>
        </div>
      </div>
    );
  }
}

class MetaBuilder extends React.Component {
  render() {
    return (
      <div class="metabuilder">
        <FileType />
        <DataModelInfo />
        <VisInfo />
        <ComparingFiles />
      </div>
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



class App extends React.Component {

 componentDidMount() {
    fetch('/api/fitsinfo')
    .then(res => res.json())
    .then((data) => {
      console.log("test is ")
      console.log(data)
    })
    .catch(
      console.log("failed")
    )
  }

  render() {
    return (
      <div className="App">
        <HeaderBar />
        <MainContent />

      </div>
    );
  }
}

export default App;
