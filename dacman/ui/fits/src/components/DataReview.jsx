import React from 'react';
import { DataGrid } from '@material-ui/data-grid';
import { WorkbenchCard } from './WorkbenchCard';
import { Button } from '@material-ui/core';


function DataReview({
    index, title, datasets_names, datasets_shapes, columns, rows,
    buttonText, actionType, dispatch}) {

  console.log("DataReview - datasets_names:", datasets_names);
  console.log("DataReview - datasets_shapes:", datasets_shapes);

  var short_description = null;

  if (datasets_names.length > 1) {
    short_description = (
      <span className="short_description">
        <span>{datasets_names[0]}, and other files</span>
      </span>
    );
  } else {
    let n_samples = Math.min(datasets_shapes[0][0], 100);
    short_description = (
      <span className="short_description">
        <span>{datasets_names[0]}</span><span>rows 1-{n_samples} of {datasets_shapes[0][0]}</span>
      </span>
    );
  }

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
