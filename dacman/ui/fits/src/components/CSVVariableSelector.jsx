import React, { useReducer } from "react";
import MaterialTable from 'material-table';

import { WorkbenchCard } from './WorkbenchCard';
import Button from "@material-ui/core/Button";


function CSVVariableSelector({ variables, dispatch }) {
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
  //onSelectionChange={(rows) => dispatch(handleChange(rows))}

  let varNames = []

  function addVariables(varNames) {
    let showVars = new Array(varNames.length).fill(false);
    if (showVars.length > 0) showVars[0] = true;
    console.log(varNames);
    console.log(showVars);
    return {
      type: 'ADD_VARS_TO_FLAG',
      payload: {
        varNames: varNames,
        showVarCard: showVars
      }
    };
  }

  return (
    <WorkbenchCard
      key="card-2"
    >
      <MaterialTable
        title="Choose Variables to flag"
        columns={columnDefs}
        data={values}
        options={{
          selection: true
        }}
        onSelectionChange={(rows) => varNames = rows.map((row) => (row.variable_name))}
      />
      <Button
        variant="contained"
        color="primary"
        onClick={() => { dispatch(addVariables(varNames)) }}
      >
        Next
      </Button>
    </WorkbenchCard>
  )
}

export {
  CSVVariableSelector
}
