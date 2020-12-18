import React from 'react';
import { DataGrid } from '@material-ui/data-grid';
import { WorkbenchCard } from './WorkbenchCard';
import { Button } from '@material-ui/core';


function DataReview({index, rows, columns, dispatch}) {
  return (
    <WorkbenchCard
      key={`card-${index}`}
      title="Data Review"
    >
      <div style={{ height: 350, width: '100%' }}>
        <DataGrid rows={rows} columns={columns} pageSize={5} />
      </div>
      <Button
        variant="contained"
        color="primary"
        onClick={e => dispatch({type: 'CHOOSE_VARS_TO_FLAG'})}>
        Next
      </Button>
    </WorkbenchCard>
  );
}

export {
  DataReview
}
