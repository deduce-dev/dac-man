import React, { useReducer } from "react";
import { MainLayout } from './Layout'
import { WorkbenchCard } from './WorkbenchCard';
import { FileUploader } from './FileUploader';
import { DataReview } from './DataReview';
import { Typography, Container, Grid } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';

import { CSVVariableSelector } from './CSVVariableSelector';
import { VariableFlaggingDetails } from './VariableFlaggingDetails';

import { useStyles } from '../common/styles';

function createData(datetime, WindDir, Windspeed_ms, temp_f, dewp_f) {
  return { datetime, WindDir, Windspeed_ms, temp_f, dewp_f };
}

const initialState = {
  showDataReview: false,
  showCSVVariableSelector: false,
  dataReview: {
    columns: [],
    rows: []
  },
  allDatasetVars: [],
  selectedVarsDetails: {
    atVar: -1,
    selectedVars: [],
    showVarCard: [],
  }
};

function reducer(state, action) {
  switch (action.type) {
    case 'UPLOAD_FILE':
      return {
        ...state,
        showDataReview: true,
        dataReview: action.payload
      };
    case 'CHOOSE_VARS_TO_FLAG':
      return {
        ...state,
        showCSVVariableSelector: true,
        allDatasetVars: action.payload
      };
    case 'SHOW_VARS_TO_FLAG':
      return {
        ...state,
        showCSVVariableSelector: true,
        allDatasetVars: action.payload
      };
    case 'ADD_VARS_TO_FLAG':
      return {
        ...state,
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          selectedVars: [
            ...state.selectedVarsDetails.selectedVars,
            action.payload.selectedVars
          ],
          showVarCard: [
            ...state.selectedVarsDetails.showVarCard,
            action.payload.showVarCard
          ]
        }
      };
    case 'MOVE_TO_NEXT_VAR':
      let atVar = state.selectedVarsDetails.atVar + 1;
      let showVarCard = state.selectedVarsDetails.showVarCard;

      showVarCard[atVar] = true;

      return {
        ...state,
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          atVar: atVar,
          showVarCard: showVarCard
        }
      };
    case 'REMOVE_VAR_TO_FLAG':
      return {
        ...state,
        showCSVVariableSelector: true,
        allDatasetVars: action.payload
      };
    default:
      return state;
  }
}

function FlaggingView() {
  const classes = useStyles();
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <MainLayout>
      <main className={classes.content}>
        <div className={classes.toolbar} />
        <Container maxWidth="lg" className={classes.container}>
          <Grid container spacing={3}>
            <FileUploader dispatch={dispatch} />
            { state.showDataReview && (
              <DataReview
                index={2}
                rows={state.dataReview.rows}
                columns={state.dataReview.columns} />
            )}
            { state.showCSVVariableSelector && (
              <CSVVariableSelector variables={state.datasetVariables} dispatch={dispatch} />
            )}
            { state.selectedVarsDetails.selectedVars.map( (variable, i) => {
                state.selectedVarsDetails.showVarCard[i] && (
                  <VariableFlaggingDetails index={i} variable={variable} dispatch={dispatch} />
                )
              })
            }
            <WorkbenchCard
              key="card-4"
              title="Review Flagging Steps"
            >
              <Typography variant="h7" gutterBottom>
                Checking Null values for:
              </Typography>
              <Typography variant="h7" className={classes.paddedFormControl} gutterBottom>
                - TEMP_F
              </Typography>
              <Typography variant="h7" gutterBottom>
                Checking Duplicate values for:
              </Typography>
              <Typography variant="h7" className={classes.paddedFormControl} gutterBottom>
                - TEMP_F
              </Typography>
              <Button
                variant="contained"
                color="primary"
              >
                Run
              </Button>
            </WorkbenchCard>
          </Grid>
        </Container>
      </main>
    </MainLayout>
  );
}

export {
  FlaggingView
}
