import React from 'react';

import { 
    InputLabel,
    Select,
    MenuItem
 } from "@material-ui/core";


export function GenericSelector({ value, setValue, resource, ...props }) {
    const label =`Select ${resource}:`;
    return (
        <>
            <label>{label}</label>
            <input
                type="text"
                description="Select this here"
                name={resource}
                value={value}
                onChange={setValue}
                {...props}
            >
            </input>
            </>
    )
}

export function ChoiceSelector({ value, setValue, resource, choices, ...props }) {
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
                    choices.map( (c) => {
                        return <MenuItem value={c}>{c}</MenuItem>
                    })
                }
            </Select>
    </>
    )
}
