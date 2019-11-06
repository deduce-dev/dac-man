import React from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';
import {
  HashRouter as Router,
  Link
} from "react-router-dom";


class ModifiedCharts extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div class="modifiedcharts arrow_box">
        <div class="addplotlink">
          <Link to="/meta">+ Add Custom Plots/Analysis</Link>
        </div>
      </div>
    );
  }
}

class SummaryTable extends React.Component {
  constructor(props) {
    super(props);
  }


  render() {

    return (
      <table class="summarytable">
        <tr>
          <th>Base</th>
          <th>Number of Files</th>
        </tr>
        <tr>
          <td>{this.props.baseInfo.dataset_id}</td>
          <td>{this.props.baseInfo.nfiles}</td>
        </tr>
        <tr>
          <th>Revision</th>
          <th>&nbsp;</th>
        </tr>
        <tr>
          <td>{this.props.revisionInfo.dataset_id}</td>
          <td>{this.props.revisionInfo.nfiles}</td>
        </tr>
      </table>
    );
  }
}

class TopSummary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      changeData: {},
      modifiedOptions : this.getOptions(),
      addedOptions : this.getOptions(),
      deletedOptions : this.getOptions(),
      unchangedOptions : this.getOptions(),
      baseInfo : {dataset_id: '', nfiles: 0},
      revisionInfo : {dataset_id: '', nfiles: 0},
    };

    this.renderChart();
  }


  getOptions() {
    var options = {
        chart: {
          type: 'pie',
          height: 200,
          width: 200
        },
        credits: {
          enabled: false
        },
        tooltip: { enabled: false },
        title: {
          text: '',
          align: 'center',
          verticalAlign: 'middle',
          y: 9
        },
        plotOptions: {
          pie: {
            innerSize: '80%',
            dataLabels: {
                enabled: false,
            }
          }
        },
        series: [{
          data: [],
          enableMouseTracking: false
        }]
    };
    return options;
  }

  componentDidMount() {
    //this.renderChart();
  }

  renderChart() {
    fetch('/api/fitschangesummary')
    .then(res => res.json())
    .then((data) => {

      this.setState({ revisionInfo : data['revision'] });
      this.setState({ baseInfo : data['base'] });

      var total = data['counts']['added'] + data['counts']['modified'] + data['counts']['deleted'] + data['counts']['unchanged'];      

      var modifiedOptions = this.getOptions();
      var mod_count = data['counts']['modified'];
      var mtitle = "Modified<br><span class='dchartnum'>" + mod_count + "</span>";
      modifiedOptions.series[0].data = [
        { name:'Modified', y: mod_count, color: "#86B3E5" },
        { name:'Other', y: (total-mod_count), color: "#E9E7E6" }];
      modifiedOptions.title = { text: mtitle};
      this.setState({
        modifiedOptions: modifiedOptions
      });

      var addedOptions = this.getOptions();
      var add_count = data['counts']['added'];
      var atitle = "Added<br><span class='dchartnum'>" + add_count + "</span>";
      addedOptions.series[0].data = [
        { name:'Added', y: add_count, color: "#A6EA8A" },
        { name:'Other', y: (total-add_count), color: "#E9E7E6" }];
      addedOptions.title = { text: atitle};
      this.setState({
        addedOptions: addedOptions
      });

      var deletedOptions = this.getOptions();
      var del_count = data['counts']['deleted'];
      var dtitle = "Deleted<br><span class='dchartnum'>" + del_count + "</span>";
      deletedOptions.series[0].data = [
        { name:'Deleted', y: del_count, color: "#E06681" },
        { name:'Other', y: (total-del_count), color: "#E9E7E6" }];
      deletedOptions.title = { text: dtitle};
      this.setState({
        deletedOptions: deletedOptions
      });

      var unchangedOptions = this.getOptions();
      var uc_count = data['counts']['unchanged'];
      var utitle = "Unchanged<br><span class='dchartnum'>" + uc_count + "</span>";
      unchangedOptions.series[0].data = [
        { name:'Unchanged', y: uc_count, color: "#676767" },
        { name:'Other', y: (total-uc_count), color: "#E9E7E6" }];
      unchangedOptions.title = { text: utitle};
      this.setState({
        unchangedOptions: unchangedOptions
      });

    })
    .catch(
      //console.log("failed")
    )
  }

  render() {

    return (
      <div class="topsummary card">        
        <HighchartsReact highcharts={Highcharts} options={this.state.modifiedOptions} />
        <HighchartsReact highcharts={Highcharts} options={this.state.addedOptions} />
        <HighchartsReact highcharts={Highcharts} options={this.state.deletedOptions} />
        <HighchartsReact highcharts={Highcharts} options={this.state.unchangedOptions} />
        <SummaryTable revisionInfo={this.state.revisionInfo} baseInfo={this.state.baseInfo} />
      </div>
    );
  }
}


class Summary extends React.Component {

  render() {
    return (
      <div className="Summary">
   
        <TopSummary />
        <ModifiedCharts />

      </div>
    );
  }
}

export default Summary;
