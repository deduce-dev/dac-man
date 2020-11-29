import React from "react";
import { Typography } from "@material-ui/core";
import Input from '@material-ui/core/Input';
import InputAdornment from '@material-ui/core/InputAdornment';
import TextField from "@material-ui/core/TextField";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormGroup from "@material-ui/core/FormGroup";
import Checkbox from "@material-ui/core/Checkbox";

import { useStyles } from '../common/styles';

function VariableFlaggingDetails({ stage, dispatch }) {
  const classes = useStyles();

  const [state, setState] = React.useState({
    checkedA: true,
    checkedB: true,
    checkedC: false,
    checkedD: false,
    checkedE: false,
  });

  const handleChange = (event) => {
    setState({ ...state, [event.target.name]: event.target.checked });
  };

  const handleValueChange = (prop) => (event) => {
    setState({ ...state, [prop]: event.target.value });
  };

  return (
    <FormControl component="fieldset" className={classes.formControl}>
      <FormGroup>
        <FormControlLabel
          control={<Checkbox checked={state.checkedA} onChange={handleChange} name="checkedA" />}
          label="Check Null values"
        />
        <FormControlLabel
          control={<Checkbox checked={state.checkedB} onChange={handleChange} name="checkedB" />}
          label="Check Duplicate values"
        />
        <FormGroup row className={classes.paddedFormControl}>
          <FormControlLabel
            control={<Checkbox checked={state.checkedC} onChange={handleChange} name="checkedC" />}
            label="Find subsequent Duplicates"
          />
          <FormControl>
            <TextField
              id="subsequent_duplicates_n"
              value={3}
              InputProps={{
                startAdornment: <InputAdornment position="start">n =</InputAdornment>,
              }}
            />
          </FormControl>
        </FormGroup>
        <FormControlLabel
          control={<Checkbox checked={state.checkedD} onChange={handleChange} name="checkedD" />}
          label="Check Bad values"
        />
        <FormGroup row className={classes.paddedFormControl}>
          <FormControl>
            <TextField
              id="iqr_coef"
              InputProps={{
                startAdornment: <InputAdornment position="start">Range</InputAdornment>,
              }}
            />
            <TextField
              id="iqr_coef"
              InputProps={{
                startAdornment: <InputAdornment position="start">To</InputAdornment>,
              }}
            />
          </FormControl>
        </FormGroup>
        <FormControlLabel
          control={<Checkbox checked={state.checkedE} onChange={handleChange} name="checkedE" />}
          label="Check Outlier values"
        />
        <FormGroup row className={classes.paddedFormControl}>
          <FormControl>
            <TextField
              id="iqr_coef"
              value={1.5}
              InputProps={{
                startAdornment: <InputAdornment position="start">IQR Coefficient =</InputAdornment>,
              }}
            />
          </FormControl>
        </FormGroup>
      </FormGroup>
    </FormControl>
  )
}

export {
  VariableFlaggingDetails
}
