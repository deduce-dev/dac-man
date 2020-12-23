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
    case 'BAD_VALS_CHECKBOX_CHANGE':
      return {
        ...state,
        checkBadVals: {
          ...state.checkBadVals,
          checked: action.payload
        }
      };
    case 'BAD_VALS_FROM_INPUT_CHANGE':
      return {
        ...state,
        checkBadVals: {
          ...state.checkBadVals,
          range: {
            ...state.checkBadVals.range,
            low: action.payload
          }
        }
      };
    case 'BAD_VALS_TO_INPUT_CHANGE':
      return {
        ...state,
        checkBadVals: {
          ...state.checkBadVals,
          range: {
            ...state.checkBadVals.range,
            high: action.payload
          }
        }
      };
    case 'OUTLIER_CHECKBOX_CHANGE':
      return {
        ...state,
        checkOutlierVals: {
          ...state.checkOutlierVals,
          checked: action.payload
        }
      };
    case 'OUTLIER_IQR_VAL_CHANGE':
      return {
        ...state,
        checkOutlierVals: {
          ...state.checkOutlierVals,
          iqrCoef: action.payload
        }
      };
    case 'EXTREME_CHECKBOX_CHANGE':
      return {
        ...state,
        checkExtremeVals: {
          ...state.checkExtremeVals,
          checked: action.payload
        }
      };
    case 'EXTREME_IQR_VAL_CHANGE':
      return {
        ...state,
        checkExtremeVals: {
          ...state.checkExtremeVals,
          iqrCoef: action.payload
        }
      };
    default:
      return state;
  }
}

function VariableFlaggingDetails({ index, variable, isFinalVar, parentDispatch }) {
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

  const badValsCheckboxChange = (event) => {
    dispatch({
      type: 'BAD_VALS_CHECKBOX_CHANGE',
      payload: event.target.checked
    });
  };

  const badValsFromInputChange = (event) => {
    dispatch({
      type: 'BAD_VALS_FROM_INPUT_CHANGE',
      payload: event.target.value
    });
  };

  const badValsToInputChange = (event) => {
    dispatch({
      type: 'BAD_VALS_TO_INPUT_CHANGE',
      payload: event.target.value
    });
  };

  const outlierCheckboxChange = (event) => {
    dispatch({
      type: 'OUTLIER_CHECKBOX_CHANGE',
      payload: event.target.checked
    });
  };

  const outlierIqrValChange = (event) => {
    dispatch({
      type: 'OUTLIER_IQR_VAL_CHANGE',
      payload: event.target.value
    });
  };

  const extremeCheckboxChange = (event) => {
    dispatch({
      type: 'EXTREME_CHECKBOX_CHANGE',
      payload: event.target.checked
    });
  };

  const extremeIqrValChange = (event) => {
    dispatch({
      type: 'EXTREME_IQR_VAL_CHANGE',
      payload: event.target.value
    });
  };

  const moveToNextVar = () => {
    parentDispatch({
      type: "MOVE_TO_NEXT_VAR",
      payload: {
        variable: variable,
        flaggingDetails: state
      }
    });
  };

  const runFlagging = () => {
    parentDispatch({
      type: "RUN_FLAGGING",
      payload: {
        variable: variable,
        flaggingDetails: state
      }
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
            control={<Checkbox checked={state.checkBadVals.checked} onChange={badValsCheckboxChange} name="checkBadVals" />}
            label="Check Bad values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="bad_vals_range_from"
                value={state.checkBadVals.range.low}
                onChange={badValsFromInputChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">Range from</InputAdornment>,
                }}
              />
              <TextField
                id="bad_vals_range_to"
                value={state.checkBadVals.range.high}
                onChange={badValsToInputChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">To</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
          <FormControlLabel
            control={<Checkbox checked={state.checkOutlierVals.checked} onChange={outlierCheckboxChange} name="checkOutlierVals" />}
            label="Check Outlier values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="outlier_iqr_coef"
                value={state.checkOutlierVals.iqrCoef}
                onChange={outlierIqrValChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">IQR Coefficient =</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
          <FormControlLabel
            control={<Checkbox checked={state.checkExtremeVals.checked} onChange={extremeCheckboxChange} name="checkExtremeVals" />}
            label="Check Extreme values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="extreme_iqr_coef"
                value={state.checkExtremeVals.iqrCoef}
                onChange={extremeIqrValChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">IQR Coefficient =</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
        </FormGroup>
      </FormControl>
      { isFinalVar ? (
          <Button
            variant="contained"
            color="primary"
            onClick={runFlagging}
          >
            Run
          </Button>
        ) : (
        <Button
          variant="contained"
          color="primary"
          onClick={moveToNextVar}
        >
          Next
        </Button>
      )
      }
    </WorkbenchCard>
  )
}

export {
  VariableFlaggingDetails
}
