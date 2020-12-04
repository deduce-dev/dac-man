import React, { useReducer } from "react";
import MaterialTable from 'material-table';

import { WorkbenchCard } from './WorkbenchCard';
import Button from "@material-ui/core/Button";


const initialState = {};

function reducer(state, action) {
  switch (action.type) {
    case 'CHECKBOX_CHANGE':
      return {
        ...state,
        rows: action.payload 
      };
    default:
      return state;
  }
}


function CSVVariableSelector({ variables, parentdispatch }) {
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

  const [state, dispatch] = useReducer(reducer, initialState);

  function handleChange(rows) {
    console.log(rows);
    return {
      type: 'CHECKBOX_CHANGE',
      payload: rows
    }
  }

  return (
    <WorkbenchCard
      key="card-2"
    >
      <MaterialTable
        columns={columnDefs}
        title="Choose Variables to flag"
        data={values}
        options={{
          selection: true
        }}
        onSelectionChange={(rows) => dispatch(handleChange(rows))}
      />
      <Button
        variant="contained"
        color="primary"
      >
        Next
      </Button>
    </WorkbenchCard>
  )
}

export {
  CSVVariableSelector
}
