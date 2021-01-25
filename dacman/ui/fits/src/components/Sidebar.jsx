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
    function renderComparison(comparison, index) {
        const cid = index;
        return (
            <Grid key={cid} item xs={12}>
                <Paper elevation={5} className={classes.paper}>
                    <div>
                        <Typography variant="h6">
                            Comparison ID: {cid}
                        </Typography>
                        {/* <PrettyPrinter item={comparison} /> */}
                        <Typography variant="h6">
                            {comparison.data.file.A} -&gt; {comparison.data.file.B}
                        </Typography>
                        <Button color="primary">Edit</Button>
                        <Button color="primary">Summary</Button>
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
