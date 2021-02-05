import React from "react";

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


export function Sidebar({ comparisons, buildData }) {
    const classes = useStyles();
    function renderComparison(cmp, index) {
        const cid = index;
        const resultsURL = 'http://localhost:5000' + cmp.results_url;
        return (
            <Grid key={cid} item xs={12}>
                <Paper elevation={5} className={classes.paper}>
                    <div>
                        <Typography>
                            Comparison ID: {cmp.comparison_id}
                        </Typography>
                        {/* <PrettyPrinter item={comparison} /> */}
                        {/* <Button color="primary">Edit</Button> */}
                        <Button color="primary" href={resultsURL} target="_blank">Results</Button>
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
        <Typography variant="h4">Comparisons</Typography>
        <Button color="primary">
          New comparison
        </Button>
      </Box>
      <Grid container className={classes.sidebarContent} spacing={2}>
        <Grid item xs={12}></Grid>
        {comparisons.map(renderComparison)}
        <SidebarCard buildData={buildData} />
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
              Comparison parameters:
            </Typography>
            <PrettyPrinter item={buildData} />
          </div>
        </Paper>
      </Grid>
    );
}
