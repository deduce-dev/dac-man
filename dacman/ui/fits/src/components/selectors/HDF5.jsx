import React from 'react';
import { useState } from "react";

import { 
    FormGroup,
    Box,
    Typography
} from "@material-ui/core";
import {
    ToggleButtonGroup,
    ToggleButton,
} from "@material-ui/lab"
import MaterialTable from "material-table";
import { ChoiceSelector } from "./Base";
import { SAMPLE } from '../../data'


function FieldBrowser({ field, setFormData, formData }) {
    const fieldKey = "fields";
    const selFieldItems = formData[fieldKey];
    const fieldVals = SAMPLE.values;
    function setFieldItems(event, newItems) {
        setFormData({target: {name: fieldKey, value: newItems}});
    }
    function FieldItemToggle(f) {
        const displayVal = fieldVals[f];
        return (
            <ToggleButton
                value={f}
                key={f}
            >
                {f}
                <br></br>
                {displayVal}
            </ToggleButton>
        )
    }

    const data = Object.keys(fieldVals);
    return (
        <Box maxHeight={120}>

        <Typography variant="h6">
            Select field components
        </Typography>
        <ToggleButtonGroup
            value={selFieldItems}
            onChange={setFieldItems}
        >
        {
            data
            .filter(f => f.includes(field))
            .map(FieldItemToggle)
        }
        </ToggleButtonGroup>
        </Box>
    );
}


export function FileBrowser({ fields, setField }) {
    const data = [...SAMPLE.fields];
    return (

        <MaterialTable
            title="Select field"
            options={{
                search: false,
                filtering: true,
            }}
            onRowClick={(e, row) => {
                console.log(row);
                setField(row.name);
                // setFormData({target: {name: "fields", value: [...fields, row.name]}})
            }}
            columns={[
                {
                    title: "Name",
                    field: "name",
                    filtering: true
                },
                {
                    title: "Type",
                    field: "type",
                }
            ]}
            data={data}
        />
    );
}


export function SelectFields({ setFormData, formData }) {
    const [selField, setSelField] = useState("");
    
    return (
        <FormGroup row={true}>
            <FileBrowser
                setField={setSelField}
            />
            {selField && 
                <FieldBrowser
                    field={selField}
                    formData={formData}
                    setFormData={setFormData}
                />
            }
        </FormGroup>
    );
}


export function SelectAnalysisParams({ setFormData, formData }) {
    const { analysis_type, visualization_type } = formData;
    const choices = SAMPLE.choices;
    return (
        <>
            <FormGroup column="true">
                <ChoiceSelector
                    resource="analysis_type"
                    value={analysis_type}
                    choices={choices.analysis_type}
                    setValue={setFormData}
                />
                <ChoiceSelector
                    resource="visualization_type"
                    value={visualization_type}
                    choices={choices.visualization_type}
                    setValue={setFormData}
                />
            </FormGroup>
        </>
    )
}