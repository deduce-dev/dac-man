import React, {useState, useEffect} from "react";

import {
    InputLabel,
    Select,
    MenuItem,
    FormGroup,
    Typography,
    Box,
    Button,
    CircularProgress,
    LinearProgress
} from "@material-ui/core";
import CheckCircleIcon from "@material-ui/icons/CheckCircle";

import {
    ToggleButtonGroup,
    ToggleButton,
} from "@material-ui/lab"

import {
    ChoiceSelector
} from "./Base";

import { useBackendData, useBuildData } from "../api";
import { ResourceDisplay } from "../Display";
import { useForm } from "react-hooks-helper";

import MaterialTable from "material-table";


function UploadStatus({ status }) {
    return (
        <>
            {status === 'pending' && (<CircularProgress/>)}
            {status === 'error' && (<span>❌</span>)}
            {status === 'success' && (<CheckCircleIcon/>)}
        </>
    );
}


export function DatasetUpload({ file, onSuccess = console.log }) {
    const [status, setStatus] = useState("idle");
    const fileName = file.name.replace('.tar.gz', '');
    const doUpload = async () => {
        const url = '/datadiff/contents/datasets';
        setStatus("pending");
        try {
            const resp = await fetch(
                url,
                {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/octet-stream',
                        'X-File-Name': fileName,
                    },
                    body: file
                }
            );
            const data = await resp.json();
            setStatus('success');
            onSuccess(data.resource_key);
        } catch(error) {
            console.log(error);
            setStatus('error');
        }
    };

    return (
        <Box display="flex" justifyContent="space-between">
            <Typography>Size: {file.size}</Typography>
            <Typography>Name: {fileName}</Typography>
            {status === 'idle' && (<Button variant="contained" color="primary" onClick={doUpload}>Upload</Button>)}
            {status !== 'idle' && (<UploadStatus status={status}/>)}
        </Box>
    )
}


export function DatasetSelector({ value, setValue, resource, choices, ...props }) {
    const label = {
        id: `${resource}-label`,
        display: `Select ${resource}`
    };
    return (
        <>
            <InputLabel id={label.id}>{label.display}</InputLabel>
            <Select
                labelId={label.id}
                value={value}
                onChange={setValue}
                name={resource}
            >
                {
                    choices.map( (ds) => {
                        return (
                            <MenuItem key={ds.resource_key} value={ds.resource_key}>
                                <ResourceDisplay {...ds}/>
                            </MenuItem>
                        )
                    })
                }
            </Select>
    </>
    )
}



export function SelectDataset({ setFormData, formData }) {
    const { base, new: new_ } = formData;
    const {data, status} = useBackendData('/contents/datasets');
    const choices = status.OK  ? data : [];

    return (
        <>
            <FormGroup column="true">
                <DatasetSelector
                    value={base}
                    resource="base"
                    choices={choices}
                    setValue={setFormData}
                />
                <DatasetSelector
                    value={new_}
                    resource="new"
                    setValue={setFormData}
                    choices={choices}
                />
            </FormGroup>
        </>
    );
}

export function SelectDatasetFile({formData, setFormData}) {
    const { sample_file, base: sampleDatasetKey } = formData;
    // const endpoint = '/contents/datasets/' + sampleDatasetKey + '/files';
    const endpoint = `/contents/datasets/${sampleDatasetKey}/files`;
    console.log(`endpoint=${endpoint}`);
    const {data, status} = useBackendData(endpoint);
    const choices = (status.OK ? data : []).map(file => file.resource_key);
    // const choices = [];
    console.log('choices: '); console.log(choices);
    return (
        <>
            <FormGroup column="true">
                <ChoiceSelector
                    resource="sample_file"
                    value={sample_file}
                    choices={choices}
                    setValue={setFormData}
                />
            </FormGroup>
            <Typography>
                {endpoint}
            </Typography>
        </>
    );
}

export function SelectH5Component({selectedField, formData, setFormData}) {
    const { base: sampleDatasetKey, sample_file, fields: selectedComponents } = formData;
    const {data, status} = useBackendData(
        `/contents/datasets/${sampleDatasetKey}/files/${sample_file}/h5/${selectedField}/values`
    );
    function setFieldComponents(event, newItems) {
        setFormData({target: {name: "fields", value: newItems}});
    }
    function FieldComponentToggle(fckey) {
        const val = valuesMap[fckey];
        const displayVal = (val && !isNaN(val)) ? val.toFixed(5) : val;
        return (
            <ToggleButton
                value={fckey}
                key={fckey}
            >
                {fckey}
                <br></br>
                {displayVal}
            </ToggleButton>
        )
    }
    const valuesMap = status.OK ? data : [];
    const componentKeys = Object.keys(valuesMap);
    return (
        <Box maxHeight={120}>

        <Typography variant="h6">
            Select field components
        </Typography>
        <ToggleButtonGroup
            value={selectedComponents}
            onChange={setFieldComponents}
        >
        {
            componentKeys
            .filter(f => f.includes(selectedField))
            .map(FieldComponentToggle)
        }
        </ToggleButtonGroup>
        </Box>
    );
}

export function SelectH5Object({formData, setFormData}) {
    const { base: sampleDatasetKey, sample_file, fields } = formData;
    const [selectedField, setSelectedField] = useState("");
    const {data, status} = useBackendData(
        `/contents/datasets/${sampleDatasetKey}/files/${sample_file}/h5`
    );
    const choices = status.OK ? data : [];
    return (
        <FormGroup row={true}>
        <MaterialTable
            options={{
                search: false,
                filtering: true,
            }}
            onRowClick={(e, row) => {
                    setSelectedField(row.resource_key);
                }
            }
            columns={[
                {
                    title: "Name",
                    field: "resource_key",
                    filtering: true
                },
                {
                    title: "Data type",
                    field: "dtype",
                },
                {
                    title: "Number of dimensions",
                    field: "ndim",
                },
                {
                    title: "Shape",
                    field: "shape",
                    render: (rowdata) => rowdata.shape.join("×")
                }
            ]}
            data={choices}
        />
        {selectedField && 
            <SelectH5Component
                formData={formData}
                setFormData={setFormData}
                selectedField={selectedField}
            />
        }
        </FormGroup>
    );
};