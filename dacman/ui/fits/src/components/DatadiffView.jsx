import React, { useState, useEffect } from "react";

import { useParams, useHistory, Route } from "react-router-dom";
import { useForm } from "react-hooks-helper";
import { VegaLite } from 'react-vega';
import { useDropzone } from "react-dropzone";

import { MainLayout } from './Layout';
import { WorkbenchContainer, WorkbenchCard } from "./Workbench";
import { Sidebar } from './Sidebar';
import { Builder } from './Builder';
import { Loading, SubmittedComparison, } from "./Display";
import { useBackendData, useBackendDispatch } from "./api";
import { FileUploaderContainer } from "./FileUploader"
import { Typography } from "@material-ui/core";
import { DatasetUpload } from "./selectors/Dataset";


const BUILD_DATA = {
    base: '',
    new: '',
    sample_file: '',
    fields: [],
    analysis_type: '',
    visualization_type: '',
    uploaded_datasets: [],
};


function DatasetsUpload({ formData, setFormData }) {
  const [beingUploaded, setBeingUploaded] = useState([]);

  const {
    acceptedFiles,
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject
  } = useDropzone({ 
    maxFiles:1,
    accept: '.tar.gz',
    onDropAccepted: (files) => {
      setBeingUploaded([...beingUploaded, ...files]);
    }
  });
  const markSuccessfulUpload = (resKey) => {
    const {uploaded_datasets: uploaded} = formData;
    setFormData({target: {name: "uploaded_datasets", value: [...uploaded, resKey]}});
  };

  return (
    <WorkbenchCard
      key="card-initial"
      title="Choose dataset file (tar.gz archive) to upload"
    >
      <div className="container">
        <FileUploaderContainer {...getRootProps({isDragActive, isDragAccept, isDragReject})}>
            <input {...getInputProps()} />
            <Typography>
              Drag and drop a file here, or click to select file
              <br/><em>(Only 1 file can be selected at a time)</em>
            </Typography>
        </FileUploaderContainer>
      </div>
        {beingUploaded.map(
          (file, idx) => {
            console.log(file);
            console.log(idx);
            console.log(beingUploaded);
            return (<DatasetUpload key={idx} file={file} onSuccess={markSuccessfulUpload}/>);
          }
        )}
    </WorkbenchCard>
  )
}


function RunComparison(buildData) {
  const {data, status} = useBackendDispatch(
    '/comparisons',
    buildData
  );
  return (
    <>
      {status.OK ? <SubmittedComparison {...data}/> : <Loading/>}
    </>
  );
}

export function BuildComparisonView() {
  const [buildData, setBuildData] = useForm(BUILD_DATA);
  const history = useHistory();

  return (
    <MainLayout>
      <WorkbenchContainer>
        <DatasetsUpload formData={buildData} setFormData={setBuildData}/>
        <Builder formData={buildData} setFormData={setBuildData} dispatch={() => history.push('/datadiff/build/run')}/>
        <Route path='/datadiff/build/run'>
          <RunComparison {...buildData}/>
        </Route>
      </WorkbenchContainer>
      <Sidebar buildData={buildData}/>
    </MainLayout>
  );
}


export function ShowResultsView() {
  const { cid } = useParams();
  const {status, data: specData} = useBackendData(`/comparisons/${cid}/results`);

  return (
    <MainLayout>
      <WorkbenchContainer>
        <WorkbenchCard>
          <Typography variant="h6" display="inline">
            Comparison <kbd>{cid}</kbd>
          </Typography>
          {status.OK ? <VegaLite spec={specData}/> : <Loading/>}
        </WorkbenchCard>
      </WorkbenchContainer>
      <Sidebar buildData={{}}/>
    </MainLayout>
  );
}