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
          testing that
      </div>
    );
  }
}

class TopSummary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      changeData: {},
      modifiedOptions : this.getModifiedOptions(),
      addedOptions : this.getAddedOptions()
    };
  }

  getModifiedOptions() {
    var modifiedOptions = {
        chart: {
          renderTo: 'container',
          type: 'pie',
          height: 200,
          width: 200
        },
        credits: {
          enabled: false
        },
        title: {
          text: ''
        },
        plotOptions: {
          pie: {
            innerSize: '60%',
            dataLabels: {
                enabled: false,
            }
          }
        },
        series: [{
          data: []
        }]
    };
    return modifiedOptions;
  }

  getAddedOptions() {
    var addedOptions = {
        chart: {
          renderTo: 'container',
          type: 'pie',
          height: 200,
          width: 200
        },
        credits: {
          enabled: false
        },
        title: {
          text: ''
        },
        plotOptions: {
          pie: {
            innerSize: '60%',
            dataLabels: {
                enabled: false,
            }
          }
        },
        series: [{
          data: []
        }]
    };
    return addedOptions;
  }

  componentDidMount() {
    fetch('/api/fitschangesummary')
    .then(res => res.json())
    .then((data) => {
      console.log(data);
      var total = data['counts']['added'] + data['counts']['modified'] + data['counts']['deleted'] + data['counts']['unchanged'];
      

      var modifiedOptions = this.getModifiedOptions();
      var mod_count = data['counts']['modified'];
      modifiedOptions.series[0].data = [['Modified', mod_count], ['Other', (total-mod_count)]];
      this.setState({
        modifiedOptions: modifiedOptions
      });

      var addedOptions = this.getAddedOptions();
      var add_count = data['counts']['added'];
      addedOptions.series[0].data = [['Added', add_count], ['Other', (total-add_count)]];
      this.setState({
        addedOptions: addedOptions
      });

    })
    .catch(
      console.log("failed")
    )
  }

  render() {

    return (
      <div class="topsummary card">
        <HighchartsReact highcharts={Highcharts} options={this.state.modifiedOptions} />
        <HighchartsReact highcharts={Highcharts} options={this.state.addedOptions} />
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
