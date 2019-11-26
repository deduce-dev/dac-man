import React from 'react';
import {
  HashRouter as Router,
  Link
} from "react-router-dom";


class FileType extends React.Component {

  constructor(props) {
    super(props);
    this.handleSelectFileFormat = this.handleSelectFileFormat.bind(this);
  }

  handleSelectFileFormat(e) {
    this.props.onSelectFileFormat(e.target.value);
  }

  render() {
    return (
      <div class="card column">
        <div class="input-group">
          <label>File Format for Comparison</label>
          <select id="file_format" onChange={this.handleSelectFileFormat}>
            <option value="" selected="selected"></option>
            <option value="fits">fits</option>
            <option value="csv" >csv</option>
          </select>
        </div>
      </div>
    );
  }
}

class DataModelInfo extends React.Component {
  constructor(props) {
    super(props);
    this.handleHduSelect = this.handleHduSelect.bind(this);
    this.handleSelectFile = this.handleSelectFile.bind(this);

    this.state = {
      exampleFile: ""
    };
  }

  handleHduSelect(e) {
    this.props.onHduSelectChange(e.target.id);
  }

  handleSelectFile(e) {
    this.setState({ 
      exampleFile : e.target.value
    });
  }

  render() {
    if (this.props.fileFormat == "fits") {
      return (
        <div class="card column">
          <div class="card-title">Data Model Information</div>
          <div class="card-subsection">
            <div class="input-group">
              <label>Select Example File</label>
              <select id="file" onChange={this.handleSelectFile}>
                <option value="" selected="selected"></option>
                <option value="spCFrame-b1-00161868.fits" >spCFrame-b1-00161868.fits</option>
              </select>
            </div>
          </div>

         { this.state.exampleFile != "" &&
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
                {this.props.hdus.map((hdu) => (
                  <tr>
                    <td><input type="checkbox"  id={hdu[0]} name={hdu[0]} onChange={this.handleHduSelect} /></td>
                    <td>{hdu[0]}</td>
                    <td>{hdu[1]}</td>
                    <td>{hdu[3]}</td>
                    <td>({hdu[5][0]},{hdu[5][1]})</td>
                    <td><input type="text" /></td>
                  </tr>
                  ))}
                </tbody>
              </table>
            </div>
          }
        </div>
      );
    } else {
      return (null);
    }
  }
}

class VisInfo extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    if (this.props.selectedHDUS.length !== 0) {
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
              {this.props.selectedHDUS.map((index) => (
                <tr>
                  <td>{this.props.hdus[index][1]}</td>
                  <td>
                      <select>
                        <option value="" selected="selected">array2 - array1</option>
                      </select>
                  </td>
                  <td>
                    <select>
                        <option value="" selected="selected">histogram</option>
                      </select>
                  </td>
                </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      );
    } else {
      return (null);
    }
  }
}

class ComparingFiles extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {

    if (this.props.selectedHDUS.length !== 0) {
      return (
        <div class="card column">
          <div class="card-title">Comparing Files</div>
          <div class="radio-group">
            <input type="radio" />
            <label>Comparing 2 Files</label>
            <input type="radio" checked="checked"/>
            <label>Comparing Multiple Files/Directories</label>
          </div>
          <div class="input-group">
            <label>Compare Files</label>
            <input type="text" value="*/*/spPlate*.fits"/>
          </div>
        </div>
      );
    } else {
      return (null);
    }
  }
}

class MainContent extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      fileFormat: ""
    };
    this.onSelectFileFormat = this.onSelectFileFormat.bind(this);
  }


  onSelectFileFormat(format) {
    this.setState({ 
      fileFormat : format
    });
  }

  render() {
    return (
      <div class="maincontent flex-body">
          <SideBar fileFormat={this.state.fileFormat} />
          <MetaBuilder 
            hdus={this.props.hdus} 
            fileFormat={this.state.fileFormat} 
            onSelectFileFormat={this.onSelectFileFormat}
          /> 
      </div>
    );
  }
}

class SideBar extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div class="sidebar flex-sidebar"> 
        <div class="column sidebar_column">
          <div class="return">
            <Link to="/"><i className='material-icons' style={{fontSize: '18px', width: '30px', verticalAlign: 'middle'}}>arrow_back_ios</i>Return to Overview</Link>
          </div>
          <div class="comparators">
            <div class="comparator-section-title">Custom Comparators</div>
            <div class="comparator-name current_comparator arrow_box_right">{this.props.fileFormat} comparator</div>
          </div>
          
          <button class="runbutton">
          RUN COMPARISONS
          </button>
        </div>
      </div>
    );
  }
}

class MetaBuilder extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      selectedHDUS: []
    };
    this.onHduSelectChange = this.onHduSelectChange.bind(this);
  }

  onHduSelectChange(index) {
    if (this.state.selectedHDUS.includes(index)) {
      console.log("index is included" + index)
      this.setState({
        selectedHDUS: this.state.selectedHDUS.filter((i) => i !== index)
      });   
    } else {
      const list = this.state.selectedHDUS.concat(index);
      this.setState({
        selectedHDUS: list
      }); 
    }
    
  }




  render() {
    return (
      <div class="metabuilder">
        <FileType onSelectFileFormat={this.props.onSelectFileFormat}/>
        <DataModelInfo 
          hdus={this.props.hdus} 
          selectedHDUS={this.state.selectedHDUS} 
          onHduSelectChange={this.onHduSelectChange} 
          fileFormat={this.props.fileFormat}
        />
        <VisInfo 
          hdus={this.props.hdus} 
          selectedHDUS={this.state.selectedHDUS}
        />
        <ComparingFiles selectedHDUS={this.state.selectedHDUS} />
      </div>
    );
  }
}






class MainMetaBuilder extends React.Component {

  state = {
    hdus: []
  }

  componentDidMount() {
    fetch('/api/fitsinfo')
    .then(res => res.json())
    .then((data) => {
      this.setState({ hdus: data })
    })
    .catch(
      console.log("failed")
    )
  }

  render() {
    return (
      <div className="MainMetaBuilder">
   
        <MainContent hdus={this.state.hdus}/>

      </div>
    );
  }
}

export default MainMetaBuilder;
