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
    SelectDataset,
    SelectDatasetFile,
    SelectH5Object
} from "./selectors/Dataset";

import {
    SelectFields,
    SelectAnalysisParams
} from "./selectors/HDF5";


const STEPS = [
    {
        action: "select",
        resource: "dataset",
        title: "Select dataset to compare",
        component: SelectDataset
    },
    {
        action: "select",
        resource: "sample_file",
        title: "Select sample file",
        component: SelectDatasetFile
    },
    {
        action: "select",
        resource: "fields",
        title: "Select HDF5 variables to compare",
        component: SelectH5Object
    },
    {
        action: "select",
        resource: "analysis_params",
        title: "Set analysis parameters",
        component: SelectAnalysisParams
    },
];


export function Builder ({ formData, setFormData, dispatch }) {
    const { index, step, navigation } = useStep({ initialStep: 0, steps: STEPS });
    const indexLast = STEPS.length - 1;
    const isBuilding = index < indexLast;
    console.log(`isBuilding=${isBuilding} (index=${index}, indexLast=${indexLast})`);
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
                {isBuilding ? "Prev" : "Back to Editing"}
            </Button>
            <Button
                variant="contained"
                color="primary"
                onClick={isBuilding ? next: dispatch}
            >
                {isBuilding ? "Next" : "Run Comparison"}
            </Button>
        </>
    )
}