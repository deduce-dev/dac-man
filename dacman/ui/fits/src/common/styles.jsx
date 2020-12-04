import { makeStyles } from "@material-ui/core/styles";

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
  },
  formControl: {
    margin: theme.spacing(1),
    minWidth: 480,
  },
  paddedFormControl: {
    padding: theme.spacing(2),
  },
}));


export {
  useStyles
}