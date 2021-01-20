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

import axios from 'axios';


function createData(datetime, WindDir, Windspeed_ms, temp_f, dewp_f) {
  return { datetime, WindDir, Windspeed_ms, temp_f, dewp_f };
}

const initialState = {
  showFileUploader: true,
  showCSVVariableSelector: false,
  dataReview: {
    show: false,
    dataset_name: null,
    columns: [],
    rows: [],
    datasetVars: [],
    datasetVarsTemplate: []
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
    data_id: null, 
    columns: [],
    rows: [],
    downloadClicked: false
  }
};

function reducer(state, action) {
  switch (action.type) {
    case 'UPLOAD_FILE':
      return {
        ...state,
        dataReview: action.payload,
        selectedVarsDetails: {
          ...initialState.selectedVarsDetails
        },
        resultsReview: {
          ...initialState.resultsReview
        }
      };
    case 'CHOOSE_VARS_TO_FLAG':
      return {
        ...state,
        showCSVVariableSelector: true
      };
    case 'ADD_VARS_TO_FLAG':
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
      if (atVar >= showVarCard.length - 1) {
        varDetailsFinished = true;
      }
      
      showVarCard[atVar] = true;

      return {
        ...state,
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          atVar: atVar,
          varDetailsFinished: varDetailsFinished,
          showVarCard: showVarCard,
          flaggingDetails: [
            ...state.selectedVarsDetails.flaggingDetails,
            action.payload.flaggingDetails
          ]
        }
      };
    case 'SENT_REQUEST':
      return {
        ...state,
        showCSVVariableSelector: false,
        dataReview: {
          ...state.dataReview,
          show: false
        },
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          show: false
        },
        resultsReview: {
          ...state.resultsReview,
          show: false
        }
      };
    case 'RUN_FLAGGING':
      return {
        ...state,
        showFileUploader: false,
        showCSVVariableSelector: false,
        dataReview: {
          ...state.dataReview,
          show: false
        },
        selectedVarsDetails: {
          ...state.selectedVarsDetails,
          show: false
        },
        resultsReview: {
          ...state.resultsReview,
          show: true,
          data_id: action.payload.response.folder_id,
          columns: action.payload.response.data.columns,
          rows: action.payload.response.data.rows
        }
      };
    case 'DOWNLOAD_RESULTS':
      return {
        ...state,
        showFileUploader: true,
        resultsReview: {
          ...state.resultsReview,
          show: false,
          downloadClicked: true
        }
      };
    default:
      return state;
  }
}

function FlaggingView() {
  const classes = useStyles();
  const [state, dispatch] = useReducer(reducer, initialState);

  if (state.resultsReview.downloadClicked && state.resultsReview.data_id != null) {
    axios({
      url: '/flagging/download/' + state.resultsReview.data_id,
      method: 'POST',
      responseType: 'blob', // important
    })
    .then((response) => {
      const downloadUrl = window.URL.createObjectURL(new Blob([response.data] , { type: 'application/gzip' }));
      const link = document.createElement('a');

      link.href = downloadUrl;
      link.setAttribute('download', 'flagged_variables.csv.gz'); //any other extension
      document.body.appendChild(link);
      link.click();
      link.remove();
    })
    .catch((error) => {
      console.log(error);
    });
  }

  return (
    <MainLayout>
      <main className={classes.content}>
        <div className={classes.toolbar} />
        <Container maxWidth="lg" className={classes.container}>
          <Grid container spacing={3}>
            { state.showFileUploader && (
              <FileUploader dispatch={dispatch} />
            )}
            { state.dataReview.show && (
              <DataReview
                index={2}
                title={'Data Review'}
                rows={state.dataReview.rows}
                columns={state.dataReview.columns}
                buttonText={'Next'}
                actionType={'CHOOSE_VARS_TO_FLAG'}
                dispatch={dispatch} />
            )}
            { state.showCSVVariableSelector && (
              <CSVVariableSelector
                columns={state.dataReview.datasetVarsTemplate}
                data={state.dataReview.datasetVars} 
                dispatch={dispatch} />
            )}
            { state.selectedVarsDetails.show && state.selectedVarsDetails.varNames.map( (variable, i) => (
                state.selectedVarsDetails.showVarCard[i] && (
                  i >= state.selectedVarsDetails.varNames.length-1 ? (
                    <VariableFlaggingDetails
                      index={i}
                      variable={variable}
                      isFinalVar={true}
                      varNames={state.selectedVarsDetails.varNames}
                      flaggingDetails={state.selectedVarsDetails.flaggingDetails}
                      dataset_name={state.dataReview.dataset_name}
                      parentDispatch={dispatch} />
                  ) : (
                    <VariableFlaggingDetails
                      index={i}
                      variable={variable}
                      isFinalVar={false}
                      varNames={null}
                      flaggingDetails={null}
                      dataset_name={null}
                      parentDispatch={dispatch} />
                  )
                )
              ))
            }
            { state.resultsReview.show && (
              <DataReview
                index={10}
                title={'Flagged-Data Review'}
                rows={state.resultsReview.rows}
                columns={state.resultsReview.columns}
                buttonText={'Download'}
                actionType={'DOWNLOAD_RESULTS'}
                dispatch={dispatch} />
            )}
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
