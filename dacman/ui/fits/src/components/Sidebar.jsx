import React from "react";
import {
  Route,
  Link as RouterLink,
  useLocation,
  useParams
} from 'react-router-dom';

import {
    Grid,
    Paper,
    Typography,
    Button,
    Drawer,
    Box,
} from "@material-ui/core";

import {
    useStyles,
} from "../common/styles";

import { PrettyPrinter } from "./PrettyPrinter";
import { useBackendData } from "./api";
import { ComparisonDetail, ComparisonSummary, PrettyUID, Timestamp } from "./Display";


export function Sidebar({ buildData, ...other }) {
  const classes = useStyles();
  const { data, status: fetchStatus, Loading } = useBackendData('/comparisons');
  const comparisons = (fetchStatus.OK ? data : []).filter(c => c.base);
  const { cid: currentID } = useParams();
  function renderComparison(cmp, index) {
      const isFocused = cmp.resource_key === currentID;
      return (
          <Grid key={index} item xs={12}>
              <Paper elevation={5} className={classes.paper}>
                  <div>
                      <ComparisonSummary {...cmp}/>
                      { isFocused && (<ComparisonDetail {...cmp}/>)}
                      { !isFocused && <Button color="primary" component={RouterLink} to={`/datadiff/comparisons/${cmp.resource_key}/results`}>Browse Results</Button>}
                  </div>
              </Paper>
          </Grid>
      )
  };
  return (
    <Drawer
      className={classes.drawer}
      variant="permanent"
      anchor="right"
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <div className={classes.toolbar} />
      <Box display="flex" justifyContent="space-between">
        <Typography variant="h4">History</Typography>
        <Button color="primary" component={RouterLink} to={`/datadiff/build`}>
          New comparison
        </Button>
      </Box>
      <Grid container className={classes.sidebarContent} spacing={2}>
        <Grid item xs={12}></Grid>
        {fetchStatus.OK ? comparisons.map(renderComparison) : <Loading/>}
        <Route path="/datadiff/build">
          <SidebarCard buildData={buildData} />
        </Route>
      </Grid>
    </Drawer>
  );
}

function SidebarCard({ buildData }) {
    const classes = useStyles();
    return (
      <Grid key="build-comparison" item xs={12}>
        <Paper elevation={5} className={classes.paper}>
          <div>
            <Typography variant="h6">
              Comparison build parameters
            </Typography>
            <PrettyPrinter item={buildData} />
          </div>
        </Paper>
      </Grid>
    );
}
