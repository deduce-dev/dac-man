import React, { useReducer } from "react";
import MaterialTable from 'material-table';

import { WorkbenchCard } from './WorkbenchCard';
import Button from "@material-ui/core/Button";


function FlaggingFinalReview({ variables, flaggingDetails, dispatch }) {

  let varsWillFlagNulls = [];
  let varsWillFlagDuplicates = [];
  let varsWillFlagBadVals = [];

  for (var i = 0; i < variables.length; i++) {
    varFlaggingDetails = flaggingDetails[i];

    if (varFlaggingDetails.checkNull == true)
      varsWillFlagNulls.push(variables[i]);
  }

  return (
    <WorkbenchCard
      key="card-4"
      title="Review Flagging Steps"
    >
      { variables.map( (variable, i) => (
          state.selectedVarsDetails.showVarCard[i] && (
            <VariableFlaggingDetails index={i} variable={variable} parentDispatch={dispatch} />
          )
        ))
      }
      <Typography variant="h6" gutterBottom>
        Checking Null values for:
      </Typography>
      <Typography variant="body1" className={classes.paddedFormControl} gutterBottom>
        - TEMP_F
      </Typography>
      <Typography variant="h6" gutterBottom>
        Checking Duplicate values for:
      </Typography>
      <Typography variant="body1" className={classes.paddedFormControl} gutterBottom>
        - TEMP_F
      </Typography>
      <Button
        variant="contained"
        color="primary"
      >
        Run
      </Button>
    </WorkbenchCard>
  )
}

export {
  CSVVariableSelector
}
