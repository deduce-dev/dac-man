import React from 'react';
import { DataGrid } from '@material-ui/data-grid';
import { WorkbenchCard } from './WorkbenchCard';
import { Button } from '@material-ui/core';


function DataReview({
    index, title, dataset_name, dataset_shape, columns, rows,
    buttonText, actionType, dispatch}) {

  let n_samples = 100;

  var short_description = (
    <span className="short_description">
      <span>{dataset_name}</span><span>rows 1-{n_samples} of {dataset_shape[0]}</span>
    </span>
  );

  return (
    <WorkbenchCard
      key={`card-${index}`}
      title={title}
      short_description={short_description}
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
