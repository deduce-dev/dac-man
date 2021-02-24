import React from "react";
import { Paper, Grid, Card, Divider } from "@material-ui/core";
import Typography from "@material-ui/core/Typography";

import { useStyles } from '../common/styles';


function WorkbenchCard({ children, title, short_description, title_align }) {
  const classes = useStyles();

  let text_align = 'left';
  if (title_align != null) {
    text_align = title_align;
  }

  const card_header = (
    short_description == null ? (
      <Typography variant="h6" align={text_align}>
        <span className="card_tite">{title}</span>
      </Typography> ) : (
      <Typography variant="h6">
        <span className="card_tite">{title}</span> {short_description}
      </Typography> )
    );
  return (
    <Grid item xs={12}>
      <Paper elevation={5} className={classes.paper}>
        {card_header}
        {children}
      </Paper>
    </Grid>
  );
}

export {
  WorkbenchCard
}
