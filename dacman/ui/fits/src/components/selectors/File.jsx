import React, {useState, useEffect} from "react";

import {
    FormGroup,
} from "@material-ui/core";

import {
    ChoiceSelector
} from "./Base"


export function SelectDir({ setFormData, formData }) {
    const { dir } = formData;
    const [choices, setChoices] = useState([]);
    useEffect( () => {
        fetch('http://localhost:5000/datadiff/content/dir')
        .then( (res) => res.json() )
        .then( (data) => {
            console.log('SelectDir::choices'); console.log(choices);
            setChoices(data || ["foo"]);
        })
    }, []);

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
    const { dir, sample_file } = formData;
    const [choices, setChoices] = useState([]);
    const params = {
        dir: dir.A,
        limit: 10
    };
    const request = new Request('http://localhost:5000/datadiff/content/file?' + new URLSearchParams(params),
        {
            mode: 'cors',
        }
    );

    useEffect( () => {
        fetch(request)
        .then( (res) => res.json() )
        .then( (data) => {
            console.log('SelectFile::choices'); console.log(choices);
            console.log('SelectFile::data'); console.log(data);
            setChoices(data);
            console.log('SelectFile::choices'); console.log(choices);
        })
        .catch( (err) => {
            alert(JSON.stringify(err));
        } )
    }, [dir.A]);


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
