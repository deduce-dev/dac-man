import React, { useReducer } from "react";
import { Typography } from "@material-ui/core";
import Input from '@material-ui/core/Input';
import InputAdornment from '@material-ui/core/InputAdornment';
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormGroup from "@material-ui/core/FormGroup";
import Checkbox from "@material-ui/core/Checkbox";
import Button from "@material-ui/core/Button";

import { WorkbenchCard } from './WorkbenchCard';
import { useStyles } from '../common/styles';

const initialState = {
  checkNull: true,
  checkDuplicates: {
    checked: true,
    checkSubsequent: false,
    subsequentNum: 3
  },
  checkBadVals: {
    checked: false,
    range: {
      low: '',
      high: ''
    }
  },
  checkOutlierVals: {
    checked: false,
    iqrCoef: 1.5
  },
  checkExtremeVals: {
    checked: false,
    iqrCoef: 3
  }
};

function reducer(state, action) {
  switch (action.type) {
    case 'CHECKBOX_CHANGE':
      return {
        ...state,
        [action.payload.name]: action.payload.checked
      };
    case 'DUPLICATES_CHECKBOX_CHANGE':
      return {
        ...state,
        checkDuplicates: {
          ...state.checkDuplicates,
          checked: action.payload
        }
      };
    case 'SUBSEQUENT_CHECKBOX_CHANGE':
      return {
        ...state,
        checkDuplicates: {
          ...state.checkDuplicates,
          checkSubsequent: action.payload
        }
      };
    case 'SUBSEQUENT_NUM_CHANGE':
      return {
        ...state,
        checkDuplicates: {
          ...state.checkDuplicates,
          subsequentNum: action.payload
        }
      };
    default:
      return state;
  }
}

function VariableFlaggingDetails({ index, variable, parentDispatch }) {
  const classes = useStyles();

  const [state, dispatch] = useReducer(reducer, initialState);

  const basicCheckboxChange = (event) => {
    dispatch({
      type: 'CHECKBOX_CHANGE',
      payload: {
        name: event.target.name,
        checked: event.target.checked
      }
    });
  };

  const duplicatesCheckboxChange = (event) => {
    dispatch({
      type: 'DUPLICATES_CHECKBOX_CHANGE',
      payload: event.target.checked
    });
  };

  const subsequentCheckboxChange = (event) => {
    dispatch({
      type: 'SUBSEQUENT_CHECKBOX_CHANGE',
      payload: event.target.checked
    });
  };

  const subsequentNumChange = (event) => {
    dispatch({
      type: 'SUBSEQUENT_NUM_CHANGE',
      payload: event.target.value
    });
  };

  return (
    <WorkbenchCard
      key={`card-${variable}`}
      title={variable}
    >
      <FormControl component="fieldset" className={classes.formControl}>
        <FormGroup>
          <FormControlLabel
            control={<Checkbox checked={state.checkNull} onChange={basicCheckboxChange} name="checkNull" />}
            label="Check Null values"
          />
          <FormControlLabel
            control={<Checkbox checked={state.checkDuplicates.checked} onChange={duplicatesCheckboxChange} name="checkDuplicates" />}
            label="Check Duplicate values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControlLabel
              control={<Checkbox checked={state.checkDuplicates.checkSubsequent} onChange={subsequentCheckboxChange} name="checkSubsequent" />}
              label="Find subsequent Duplicates"
            />
            <FormControl>
              <TextField
                id="subsequent_duplicates_n"
                value={state.checkDuplicates.subsequentNum}
                onChange={subsequentNumChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">n =</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
          <FormControlLabel
            control={<Checkbox checked={state.checkBadVals.checked} onChange={basicCheckboxChange} name="checkBadVals" />}
            label="Check Bad values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="iqr_coef"
                onChange={subsequentNumChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">From</InputAdornment>,
                }}
              />
              <TextField
                id="iqr_coef"
                onChange={subsequentNumChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">To</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
          <FormControlLabel
            control={<Checkbox checked={state.checkOutlierVals.checked} onChange={basicCheckboxChange} name="checkOutlierVals" />}
            label="Check Outlier values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="outlier_iqr_coef"
                value={state.checkOutlierVals.iqrCoef}
                onChange={subsequentNumChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">IQR Coefficient =</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
          <FormControlLabel
            control={<Checkbox checked={state.checkExtremeVals.checked} onChange={basicCheckboxChange} name="checkExtremeVals" />}
            label="Check Extreme values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="extreme_iqr_coef"
                value={state.checkExtremeVals.iqrCoef}
                onChange={subsequentNumChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">IQR Coefficient =</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
        </FormGroup>
      </FormControl>
      <Button
        variant="contained"
        color="primary"
      >
        Next
      </Button>
    </WorkbenchCard>
  )
}

export {
  VariableFlaggingDetails
}
