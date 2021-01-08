import React from 'react';
import { DataGrid } from '@material-ui/data-grid';
import { WorkbenchCard } from './WorkbenchCard';
import { Button } from '@material-ui/core';


function DataReview({index, title, columns, rows, buttonText, actionType, dispatch}) {
  return (
    <WorkbenchCard
      key={`card-${index}`}
      title={title}
    >
      <div style={{ height: 350, width: '100%' }}>
        <DataGrid columns={columns} rows={rows} pageSize={5} />
      </div>
      <Button
        variant="contained"
        color="primary"
        onClick={e => dispatch({type: actionType})}>
        {buttonText}
      </Button>
    </WorkbenchCard>
  );
}

export {
  DataReview
}
