import React from 'react';
import { DataGrid } from '@material-ui/data-grid';
import { Grid, Divider } from "@material-ui/core";
import { WorkbenchCard } from './WorkbenchCard';

import { useStyles } from '../common/styles';


function ProcessingCue({ title, file_list }) {
  const classes = useStyles();

  var styled_title = (
    <span className="title_center">
      {title}
      <Divider />
    </span>
  );

  var styled_file_list = file_list.map((filename, i) => (
    <li className={classes.uploadFileList}>{filename.path}</li>
  ));

  return (
    <WorkbenchCard
      key="card-in-progress"
      title={styled_title}
      title_align="center"
    >
      <Grid container spacing={1} style={{ height: 200, width: '100%' }}>
        <Grid item xs={6} className="lds-ring-container-container">
          <Grid container class="lds-ring-container">
            <Grid item xs={12} style={{ paddingTop: "13%" }}>
              <span style={{ color: '#5499C7', "font-weight": "bold" }}>PROCESSING</span>
            </Grid>
            <Grid item xs={12}>
              <div class="lds-ring"><div></div><div></div><div></div><div></div></div>
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={6} className="lds-ring-container-container">
          { styled_file_list.length > 0 && (
            <aside style={{ paddingLeft: "10%" }}>
              <h4>Files</h4>
              <ul>{styled_file_list}</ul>
            </aside>
          )}
        </Grid>
      </Grid>
    </WorkbenchCard>
  );
}

export {
  ProcessingCue
}
