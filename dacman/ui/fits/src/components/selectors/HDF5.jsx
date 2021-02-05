import React from 'react';
import { useState, useEffect } from "react";

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


function FieldBrowser({ field, setFormData, formData, fieldValuesData }) {
    const fieldKey = "fields";
    const selFieldItems = formData[fieldKey];

    function setFieldItems(event, newItems) {
        setFormData({target: {name: fieldKey, value: newItems}});
    }
    function FieldItemToggle(f) {
        const displayVal = fieldValuesData[f];
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

    const data = Object.keys(fieldValuesData);
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


export function FileBrowser({ fields, setField, fieldData }) {

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
            data={fieldData}
        />
    );
}


export function SelectFields({ setFormData, formData }) {
    const {dir, sample_file } = formData;
    const [selField, setSelField] = useState("");
    const [sampleData, setSampleData] = useState({});
    const params = {
        dir: dir.A,
        file: sample_file,
    };
    const request = new Request('http://localhost:5000/datadiff/content/h5?' + new URLSearchParams(params),
        {
            mode: 'cors',
        }
    );

    useEffect( () => {
        fetch(request)
        .then( (res) => res.json() )
        .then( (data) => {
            console.log('SelectFile::sampleData'); console.log(sampleData);
            console.log('SelectFile::data'); console.log(data);
            setSampleData(data);
        })
        .catch( (err) => {
            alert(JSON.stringify(err));
        })
    }, [dir.A, sample_file]); 
    
    return (
        <FormGroup row={true}>
            <FileBrowser
                setField={setSelField}
                fieldData={sampleData.fields}
            />
            {selField && 
                <FieldBrowser
                    field={selField}
                    formData={formData}
                    setFormData={setFormData}
                    fieldValuesData={sampleData.values}
                />
            }
        </FormGroup>
    );
}


export function SelectAnalysisParams({ setFormData, formData }) {
    const { analysis_type, visualization_type } = formData;
    // TODO fetch from backend (OTOH it's not essential)
    const choices = {
        analysis_type: [
            'new - base'
        ],
        visualization_type: [
            'histogram'
        ]
    };
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