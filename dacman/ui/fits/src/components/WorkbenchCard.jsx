import React from "react";
import { Paper, Grid, Card } from "@material-ui/core";
import Typography from "@material-ui/core/Typography";

import { useStyles } from '../common/styles';


function WorkbenchCard({ children, title }) {
  const classes = useStyles(); 
  return (
    <Grid item xs={12}>
      <Paper elevation={5} className={classes.paper}>
        <Typography variant="h6">
          {title}
        </Typography>
        {children}
      </Paper>
    </Grid>
  );
}

export {
  WorkbenchCard
}
