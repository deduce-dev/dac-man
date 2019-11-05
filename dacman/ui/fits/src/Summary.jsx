import React from 'react';
import Highcharts from 'highcharts';
import HighchartsReact from 'highcharts-react-official';



class ModifiedCharts extends React.Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <div class="modifiedcharts">
          
      </div>
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
      unchangedOptions : this.getOptions()
    };
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
    this.renderChart();
  }

  renderChart() {
    fetch('/api/fitschangesummary')
    .then(res => res.json())
    .then((data) => {
      console.log(data);
      var total = data['counts']['added'] + data['counts']['modified'] + data['counts']['deleted'] + data['counts']['unchanged'];
      

      var modifiedOptions = this.getOptions();
      var mod_count = data['counts']['modified'];
      var mtitle = "Modified<br><span class='dchartnum'>" + mod_count + "</span>";
      modifiedOptions.series[0].data = [
        { name:'Modified', y: mod_count, color: "#00BCD4" },
        { name:'Other', y: (total-mod_count), color: "#E9E7E6" }];
      modifiedOptions.title = { text: mtitle};
      this.setState({
        modifiedOptions: modifiedOptions
      });

      var addedOptions = this.getOptions();
      var add_count = data['counts']['added'];
      var atitle = "Added<br><span class='dchartnum'>" + add_count + "</span>";
      addedOptions.series[0].data = [
        { name:'Added', y: add_count, color: "#9CC988" },
        { name:'Other', y: (total-add_count), color: "#E9E7E6" }];
      addedOptions.title = { text: atitle};
      this.setState({
        addedOptions: addedOptions
      });

      var deletedOptions = this.getOptions();
      var del_count = data['counts']['deleted'];
      var dtitle = "Deleted<br><span class='dchartnum'>" + del_count + "</span>";
      deletedOptions.series[0].data = [
        { name:'Deleted', y: del_count, color: "#F05E61" },
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
