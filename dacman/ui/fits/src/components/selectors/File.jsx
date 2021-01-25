import React from "react";

import {
    FormGroup,
} from "@material-ui/core";

import {
    ChoiceSelector
} from "./Base"

import { SAMPLE } from "../../data";


export function SelectDir({ setFormData, formData }) {
    const { dir } = formData;
    const choices = SAMPLE.choices.dir;

    return (
        <>
            <FormGroup column="true">
                <ChoiceSelector
                    value={dir.A}
                    resource="dir.A"
                    choices={choices}
                    setValue={setFormData}
                />
                <ChoiceSelector
                    value={dir.B}
                    resource="dir.B"
                    setValue={setFormData}
                    choices={choices}
                />
            </FormGroup>
        </>
    );
}

export function SelectSampleFile({ setFormData, formData }) {
    const { sample_file } = formData;
    const choices = SAMPLE.choices.sample_file;

    return (
        <FormGroup column="true">
            <ChoiceSelector
                resource="sample_file"
                value={sample_file}
                choices={choices}
                setValue={setFormData}
            />
        </FormGroup>
    );
}
