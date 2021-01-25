import React from "react";

import { useForm, useStep } from "react-hooks-helper";
import {
    Button,
    FormGroup,
} from "@material-ui/core";

import { PrettyPrinter } from "./PrettyPrinter";
import { WorkbenchCard } from "./Workbench";
import { 
    SelectDir,
    SelectSampleFile
 } from "./selectors/File";
import {
    SelectFields,
    SelectAnalysisParams
} from "./selectors/HDF5";

import { SAMPLE } from "../data";

const STEPS = [
    {
        action: "select",
        resource: "dir",
        title: "Select directories to compare",
        component: SelectDir
    },
    {
        action: "select",
        resource: "sample_file",
        title: "Select sample file",
        component: SelectSampleFile
    },
    {
        action: "select",
        resource: "fields",
        title: "Select HDF5 variables to compare",
        component: SelectFields
    },
    {
        action: "select",
        resource: "analysis_params",
        title: "Set analysis parameters",
        component: SelectAnalysisParams
    }
];


export function Builder ({ formData, setFormData }) {
    const { index, step, navigation } = useStep({ initialStep: 0, steps: STEPS });
    const { previous, next } = navigation;
    const stepProps = { formData, setFormData };
    const Selector = PrettyPrinter;
    return (
        <>
            {STEPS
            .slice(0, index + 1)
            .map( (s, idx) => {
                const Sel = s.component;
                const title = s.title;
                console.log('step:'); console.log(s);
                return (
                    <WorkbenchCard title={title} key={`card-${idx}`}>
                        <Sel key={idx} {...stepProps}/>
                    </WorkbenchCard>
                )
            })}
            <Button
                variant="contained"
                color="primary"
                onClick={previous}
            >
                Prev
            </Button>
            <Button
                variant="contained"
                color="primary"
                onClick={next}
            >
                Next
            </Button>
        </>
    )
}