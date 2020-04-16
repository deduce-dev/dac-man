import React from "react";
import { makeStyles } from "@material-ui/core/styles";
import Drawer from "@material-ui/core/Drawer";
import AppBar from "@material-ui/core/AppBar";
import CssBaseline from "@material-ui/core/CssBaseline";
import Toolbar from "@material-ui/core/Toolbar";
import List from "@material-ui/core/List";
import Typography from "@material-ui/core/Typography";
import Divider from "@material-ui/core/Divider";
import ListItem from "@material-ui/core/ListItem";
import ListItemIcon from "@material-ui/core/ListItemIcon";
import ListItemText from "@material-ui/core/ListItemText";
import {Tab, Tabs} from "@material-ui/core";

import { Paper, Container, Grid, Card, Box } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";

import { Link as RouterLink } from "react-router-dom";

const drawerWidth = 480;

const useStyles = makeStyles(theme => ({
  root: {
    display: "flex"
  },
  appBar: {
    zIndex: theme.zIndex.drawer + 1
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
    padding: theme.spacing(2),
    backgroundColor: '#c5c5c5',
  },
  content: {
    flexGrow: 1,
    padding: theme.spacing(3)
  },
  toolbar: theme.mixins.toolbar,
  paper: {
    padding: theme.spacing(2),
    display: "flex",
    overflow: "auto",
    flexDirection: "column"
  },
  container: {
    paddingTop: theme.spacing(4),
    paddingBottom: theme.spacing(4)
  },
  sidebarContent: {
    // padding: theme.spacing(3),
  },
  appBarToolbar: {
    display: "flex", flexGrow: 1, justifyContent: "space-between"
  }
}));

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

function SidebarCard({ fileA, fileB }) {
  const classes = useStyles();
  return (
    <Paper elevation={5} className={classes.paper}>
      <div>
        <Typography variant="h6">
          {fileA} -> {fileB}
        </Typography>
        <Button color="primary" component={RouterLink} to={`/compare`}>Edit</Button>
        <Button color="primary" component={RouterLink} to={`/summary`}>Summary</Button>
      </div>
    </Paper>
  );
}

function Sidebar({cardContentItems = []}) {
    const classes = useStyles();
    const renderItem = (item, index) => {
      console.log(item)
        return (
          <Grid key={item.comparisonID} item xs={12}>
            <SidebarCard fileA={item.fileA} fileB={item.fileB} />
          </Grid>
        );
    }
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
              <Button variant="contained" color="primary" component={RouterLink} to={`/compare`}>
                Add comparison
              </Button>
            </Box>
            <Grid container className={classes.sidebarContent} spacing={2}>
              <Grid item xs={12}>
              </Grid>
              {cardContentItems.map(renderItem)}
            </Grid>
        </Drawer>
    );
}

function Workbench({items = [], itemRenderer}) {
    const classes = useStyles();
    return (
        <main className={classes.content}>
        <div className={classes.toolbar} />
        <Container maxWidth="lg" className={classes.container}>
          <Grid container spacing={3}>
              {items.map( (item, index) => {
                  return (
                      <WorkbenchCard
                        key={index}
                        title={item.title}
                      >
                        {item.component(item.props)}
                      </WorkbenchCard>
                  );
              })
            }
          </Grid>
        </Container>
      </main>
    );
}

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
  MainLayout,
  Workbench,
  Sidebar,
}