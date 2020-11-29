import React from "react";
import MaterialTable from 'material-table';


function CSVVariableSelector({ stage, dispatch }) {
  let columnDefs = [
    { title: 'Variables', field: 'variable_name' },
    { title: 'Dimensions', field: 'dimensions' },
    { title: 'Content Type', field: 'content_type' }
  ];

  let values= [
    {
        variable_name: 'datetime',
        dimensions: '(1, 105192)',
        content_type: 'String'
    },
    {
        variable_name: 'WindDir',
        dimensions: '(1, 105192)',
        content_type: 'Integer'
    },
    {
        variable_name: 'Windspeed_ms',
        dimensions: '(1, 105192)',
        content_type: 'Float'
    },
    {
        variable_name: 'TEMP_F',
        dimensions: '(1, 105192)',
        content_type: 'Integer'
    },
    {
        variable_name: 'DEWP_F',
        dimensions: '(1, 105192)',
        content_type: 'Integer'
    },
  ]

  return (
    <MaterialTable
      columns={columnDefs}
      title="Choose Variables to flag"
      data={values}
      options={{
        selection: true
      }}
    />
  )
}

export {
  CSVVariableSelector
}
