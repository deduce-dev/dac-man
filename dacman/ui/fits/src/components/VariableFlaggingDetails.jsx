import React, { useReducer } from "react";
import Grid from '@material-ui/core/Grid';
import List from '@material-ui/core/List';
import Card from '@material-ui/core/Card';
import CardHeader from '@material-ui/core/CardHeader';
import Divider from '@material-ui/core/Divider';
import ListItem from '@material-ui/core/ListItem';
import ListItemText from '@material-ui/core/ListItemText';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import InputAdornment from '@material-ui/core/InputAdornment';
import Radio from '@material-ui/core/Radio';
import RadioGroup from '@material-ui/core/RadioGroup';
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormGroup from "@material-ui/core/FormGroup";
import FormHelperText from '@material-ui/core/FormHelperText';
import FormLabel from '@material-ui/core/FormLabel';
import Checkbox from "@material-ui/core/Checkbox";
import Button from "@material-ui/core/Button";

import { WorkbenchCard } from './WorkbenchCard';
import { useStyles } from '../common/styles';

import axios from 'axios';

const initialState = {
  variable_type: 'numeric',
  checkNull: true,
  nullValues: [],
  checkDuplicates: {
    checked: true,
    subsequentDisabled: false,
    subsequentNum: 3
  },
  checkBadVals: {
    checked: false,
    disabled: false,
    range: {
      low: '',
      high: ''
    }
  },
  checkOutlierVals: {
    checked: true,
    disabled: false,
    iqrCoef: 1.5
  },
  checkExtremeVals: {
    checked: true,
    disabled: false,
    iqrCoef: 3
  }
};

function reducer(state, action) {
  switch (action.type) {
    case 'VARIABLE_TYPE_CHANGE':
      let new_state = {
        ...state,
        variable_type: action.payload
      };
      if (action.payload == 'numeric') {
        new_state = {
          ...new_state,
          checkDuplicates: {
            ...new_state.checkDuplicates,
            subsequentDisabled: false
          },
          checkBadVals: {
            ...new_state.checkBadVals,
            disabled: false
          },
          checkOutlierVals: {
            ...new_state.checkOutlierVals,
            disabled: false
          },
          checkExtremeVals: {
            ...new_state.checkExtremeVals,
            disabled: false
          }
        }
      } else {
        new_state = {
          ...new_state,
          checkDuplicates: {
            ...new_state.checkDuplicates,
            subsequentDisabled: true
          },
          checkBadVals: {
            ...new_state.checkBadVals,
            checked: false,
            disabled: true
          },
          checkOutlierVals: {
            ...new_state.checkOutlierVals,
            checked: false,
            disabled: true
          },
          checkExtremeVals: {
            ...new_state.checkExtremeVals,
            checked: false,
            disabled: true
          }
        }
      }

      return new_state;
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
    case 'ADD_NULL_VALUE':
      let newNullValues = new Set(state.nullValues);
      newNullValues.add(action.payload);
      return {
        ...state,
        nullValues: Array.from(newNullValues)
      };
    case 'DELETE_NULL_VALUE':
      let currentNullValues = new Set(state.nullValues);
      currentNullValues.delete(action.payload);
      return {
        ...state,
        nullValues: Array.from(currentNullValues)
      };
    default:
      return state;
  }
}

function VariableFlaggingDetails({
    index, project_id, variable, isFinalVar, varNames,
    flaggingDetails, dataset_name, parentDispatch }) {

  const classes = useStyles();

  const [state, dispatch] = useReducer(reducer, initialState);

  const nullInput = React.useRef(null);

  const chooseVariableType = (event) => {
    dispatch({
      type: 'VARIABLE_TYPE_CHANGE',
      payload: event.target.value
    });
  }

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

  const handleCustomNullValue = () => {
    if (nullInput.current.value) {
      dispatch({
        type: 'ADD_NULL_VALUE',
        payload: nullInput.current.value
      });
    }
  };

  const handleNullValueClick = (event) => {
    dispatch({
      type: 'DELETE_NULL_VALUE',
      payload: event.target.innerText
    });
  }

  const runFlagging = () => {
    console.log("flaggingDetails:", flaggingDetails);
    let varDetails = {
      dataset_name: dataset_name,
      varNames: [...varNames],
      flaggingDetails: [
        ...flaggingDetails,
        state
      ]
    }
    let req = axios.post('/flagging/run/' + project_id, varDetails)

    parentDispatch({type: "SENT_REQUEST" });

    req.then((response) => {
      //console.log(response.data);
      //var resData = JSON.parse(JSON.stringify(response.data));
      //var resData = JSON.parse(response.data);
      console.log("response.data:", response.data);
      parentDispatch({
        type: "RUN_FLAGGING",
        payload: {
          variable: variable,
          flaggingDetails: state,
          response: response.data
        }
      });

      parentDispatch({
        type: "DOWNLOAD_RESULTS"
      });
    })
    .catch((error) => {
      console.log(error);
    });
  };

  return (
    <WorkbenchCard
      key={`card-${variable}`}
      title={variable}
    >
      <FormControl component="fieldset" className={classes.formControl}>
        <FormGroup>
          <FormHelperText>Variable Type</FormHelperText>
          <RadioGroup row aria-label="variable_type" name="variable_type"
            defaultValue="numeric" onChange={chooseVariableType}>
            <FormControlLabel
              value="numeric"
              control={<Radio />}
              label="Numeric"
              labelPlacement="end"
            />
            <FormControlLabel
              value="string"
              control={<Radio />}
              label="String"
              labelPlacement="end"
            />
            <FormControlLabel
              value="date"
              control={<Radio />}
              label="Date"
              labelPlacement="end"
            />
          </RadioGroup>
        </FormGroup>
        <FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                checked={state.checkNull}
                onChange={basicCheckboxChange}
                name="checkNull" />
            }
            label="Check Null values"
          />
          <FormControlLabel
            control={
              <Grid
                container
                spacing={2}
                justifyContent="center"
                alignItems="center">
                <Grid item>
                  <TextField
                    inputRef={nullInput}
                    id="null_input"
                    label="Custom Null Value"
                    placeholder="e.g -999"
                    variant="outlined" />
                </Grid>
                <Grid item>
                  <Button
                    variant="outlined"
                    size="small"
                    onClick={handleCustomNullValue}
                    //disabled={!nullInput.current || !nullInput.current.value}
                    aria-label="move all right"
                  >
                    &gt;
                  </Button>
                </Grid>
                <Grid item>
                  <Card>
                    <CardHeader
                      titleTypographyProps={{variant:'subtitle1' }}
                      title='Null Values'
                    />
                    <Divider />
                    <List dense component="div" role="list">
                      {state.nullValues.map((value) => {
                        const labelId = `transfer_list_item_${value}_label`;

                        //<ListItem key={value} role="listitem" button >
                        return (
                          <ListItem key={value} role="listitem" button onClick={handleNullValueClick}>
                            <ListItemText id={labelId} primary={value} />
                          </ListItem>
                        );
                      })}
                      <ListItem />
                    </List>
                  </Card>
                </Grid>
              </Grid>
            }
          />
          <FormControlLabel
            control={
              <Checkbox
                checked={state.checkDuplicates.checked}
                onChange={duplicatesCheckboxChange}
                name="checkDuplicates" />
            }
            label="Check Duplicate values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="subsequent_duplicates_n"
                label="# of subsequent duplicates"
                disabled={(state.checkDuplicates.subsequentDisabled || !state.checkDuplicates.checked)}
                variant={(state.checkDuplicates.subsequentDisabled || !state.checkDuplicates.checked) ? 'filled' : 'outlined'}
                value={state.checkDuplicates.subsequentNum}
                onChange={subsequentNumChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">n =</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                disabled={state.checkBadVals.disabled}
                checked={state.checkBadVals.checked}
                onChange={badValsCheckboxChange}
                name="checkBadVals" />
            }
            label="Check Bad values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="bad_vals_range_from"
                disabled={!state.checkBadVals.checked}
                variant={state.checkBadVals.checked ? 'outlined' : 'filled'}
                value={state.checkBadVals.range.low}
                onChange={badValsFromInputChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">Range from</InputAdornment>,
                }}
              />
              <TextField
                id="bad_vals_range_to"
                disabled={!state.checkBadVals.checked}
                variant={state.checkBadVals.checked ? 'outlined' : 'filled'}
                value={state.checkBadVals.range.high}
                onChange={badValsToInputChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">To</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                disabled={state.checkOutlierVals.disabled}
                checked={state.checkOutlierVals.checked}
                onChange={outlierCheckboxChange} name="checkOutlierVals" />
            }
            label="Check Outlier values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="outlier_iqr_coef"
                disabled={!state.checkOutlierVals.checked}
                variant={state.checkOutlierVals.checked ? 'outlined' : 'filled'}
                value={state.checkOutlierVals.iqrCoef}
                onChange={outlierIqrValChange}
                InputProps={{
                  startAdornment: <InputAdornment position="start">IQR Coefficient =</InputAdornment>,
                }}
              />
            </FormControl>
          </FormGroup>
          <FormControlLabel
            control={
              <Checkbox
                disabled={state.checkExtremeVals.disabled}
                checked={state.checkExtremeVals.checked}
                onChange={extremeCheckboxChange}
                name="checkExtremeVals" />
            }
            label="Check Extreme values"
          />
          <FormGroup row className={classes.paddedFormControl}>
            <FormControl>
              <TextField
                id="extreme_iqr_coef"
                disabled={!state.checkExtremeVals.checked}
                variant={state.checkExtremeVals.checked ? 'outlined' : 'filled'}
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
