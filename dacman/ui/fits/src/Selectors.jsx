import React, {useState, useEffect} from 'react';
import { Paper, Container, Grid, Card, Box, Typography } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import MenuItem from "@material-ui/core/MenuItem";
import Select from "@material-ui/core/Select";
import FormHelperText from "@material-ui/core/FormHelperText";
import FormControl from "@material-ui/core/FormControl";
import FormControlLabel from "@material-ui/core/FormControlLabel";
import FormGroup from "@material-ui/core/FormGroup";
import Checkbox from "@material-ui/core/Checkbox";

import MaterialTable from 'material-table';


function TextSelector({description, setSelectedValue}) {
    return (
        <TextField
          // id={`${res}-${stage.action}-A`}
          label={description}
          helperText={description}
          variant="outlined"
          onChange={e => setSelectedValue(e.target.value)}
        />
    )  
}

function BoolSelector({name, description, value, dispatch}) {
    const [selected, setSelected] = useState(value);
    const handleChange = (e) => {
        let val = e.target.checked;
        setSelected(val);
        dispatch({type: 'setFormData', name: name, value: val});
    }
    return (
        <FormControlLabel
          control={
                <Checkbox
                    // TODO think if we need/want to pass the initial value as well
                    checked={selected}
                    onChange={handleChange}
                    // inputRef={inputRef}
                    // defaultChecked={inputRef.current.checked}
                />
            }
          label={description}
        />
    )
}

function ChoiceSelector({name, description, choices, dispatch}) {

    // console.log(`ChoiceSelector.props=`); console.log(props)
    // console.log(`ChoiceSelector.description=`); console.log(description)
    // console.log(`ChoiceSelector.setSelectedValue=`); console.log(setSelectedValue)
    function renderChoice(item, index) {
        return (
            <MenuItem key={index} value={item}>{item}</MenuItem>
        );
    };

    // make sure that the first choice is always a placeholder value
    choices = ['---', ...choices];

    const [selected, setSelected] = useState(choices[0]);
    const handleChange = (e) => {
        let val = e.target.value;
        setSelected(val);
        dispatch({type: 'setFormData', name: name, value: val});
    }

    return (
        // <FormControl className={classes.formControl}>
        <FormControl>
          <Select
              variant="outlined"
            //   TODO decide if this needs to be preselected or not
              value={selected}
              onChange={handleChange}
            //   defaultValue={props.choices[0]}
            //   inputRef={inputRef}
            >
            {choices.map(renderChoice)}
          </Select>
          <FormHelperText>{description}</FormHelperText>
        </FormControl>
    )
}

function FixedSelector({name, description, value, dispatch}) {
    return (
        <Typography>
            <code>
                {value}
            </code>
        </Typography>
    )
}

function TableSelector({name, description, choices, dispatch, ...props}) {

    const handleChange = (rows) => {
        let singleRow = rows[0];
        dispatch({type: 'setFormData', name: name, value: {...singleRow}});
    }

    return (
        <MaterialTable
            columns={props.columns}
            title={description}
            data={choices}
            options={{
                selection: true
            }}
            // TODO also somehow force the fact that only a single entry should be selected
            // for the moment, we can fall back on always returning the first selected row
            onSelectionChange={handleChange}
        />
    )
}

export {
    FixedSelector,
    ChoiceSelector,
    BoolSelector,
    TableSelector,
}