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
  showCSVVariableSelector: false,
  dataReview: {
    show: false,
    columns: [],
    rows: [],
    datasetVars:[]
  },
  selectedVarsDetails: {
    show: true,
    atVar: -1,
    varDetailsFinished: false,
    varNames: [],
    showVarCard: [],
    flaggingDetails: []
  },
  resultsReview: {
    show: false,
    columns: [],
    rows: []
  }
};

function reducer(state, action) {
  switch (action.type) {
    case 'UPLOAD_FILE':
      return {
        ...state,
        dataReview: action.payload
      };
    case 'CHOOSE_VARS_TO_FLAG':
      return {
        ...state,
        showCSVVariableSelector: true
      };
    case 'ADD_VARS_TO_FLAG':
      console.log({
        ...state,
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          atVar: 0,
          varNames: action.payload.varNames,
          showVarCard: action.payload.showVarCard
        }});
      return {
        ...state,
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          atVar: 0,
          varNames: action.payload.varNames,
          showVarCard: action.payload.showVarCard
        }
      };
    case 'MOVE_TO_NEXT_VAR':
      let atVar = state.selectedVarsDetails.atVar + 1;
      let showVarCard = state.selectedVarsDetails.showVarCard;

      let varDetailsFinished = false;
      if (atVar >= showVarCard.length) {
        varDetailsFinished = true;
      }
      
      showVarCard[atVar] = true;

      console.log({
        ...state,
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          atVar: atVar,
          varDetailsFinished: varDetailsFinished,
          showVarCard: showVarCard,
          flaggingDetails: action.payload.flaggingDetails
        }
      });
      return {
        ...state,
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          atVar: atVar,
          varDetailsFinished: varDetailsFinished,
          showVarCard: showVarCard,
          flaggingDetails: action.payload.flaggingDetails
        }
      };
    case 'RUN_FLAGGING':
      //let temp = ;
      return {
        ...state,
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          show: false,
        },
        resultsReview: {
          ...state.resultsReview
        }
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
            { state.dataReview.show && (
              <DataReview
                index={2}
                rows={state.dataReview.rows}
                columns={state.dataReview.columns} 
                dispatch={dispatch} />
            )}
            { state.showCSVVariableSelector && (
              <CSVVariableSelector
                variables={state.dataReview.datasetVars} 
                dispatch={dispatch} />
            )}
            { state.selectedVarsDetails.show && state.selectedVarsDetails.varNames.map( (variable, i) => (
                state.selectedVarsDetails.showVarCard[i] && (
                  <VariableFlaggingDetails
                    index={i}
                    variable={variable}
                    parentDispatch={dispatch}
                    isFinalVar={state.selectedVarsDetails.varDetailsFinished} />
                )
              ))
            }
            {/*
            { state.selectedVarsDetails.varDetailsFinished && (
                <FlaggingFinalReview
                  variables={state.selectedVarsDetails.varNames}
                  flaggingDetails={state.selectedVarsDetails.flaggingDetails} />
            )}
            */}
          </Grid>
        </Container>
      </main>
    </MainLayout>
  );
}

export {
  FlaggingView
}
