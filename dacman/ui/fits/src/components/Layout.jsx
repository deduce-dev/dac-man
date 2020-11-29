import React from "react";
import { Box } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import AppBar from "@material-ui/core/AppBar";
import Toolbar from "@material-ui/core/Toolbar";
import Typography from "@material-ui/core/Typography";

import { useStyles } from '../common/styles';


function MainLayout(props) {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <AppBar position="fixed" className={classes.appBar}>
        <Toolbar className={classes.appBarToolbar}>
          {/* <Typography flexGrow={1} variant="h6"> */}
          <Box>
            <Typography variant="h6">
              Deduce
            </Typography>
          </Box>
          <Box>
            <Button color="inherit">About</Button>
            <Button color="inherit">Documentation</Button>
          </Box>
        </Toolbar>
      </AppBar>
      {props.children}
    </div>
  );
}


export {
  MainLayout
}
