import React, { useState, useEffect } from "react";

import { useParams, useHistory, Route } from "react-router-dom";
import { useForm } from "react-hooks-helper";
import { VegaLite } from 'react-vega';

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



export function DatadiffView() {
  const [buildData, setBuildData] = useForm(BUILD_DATA);
  const [comparisons, setComparisons] = useState([]);
  const [pending, setPending] = useState([]);
  const [completed, setCompleted] = useState(0);

  const requests = {
    getComparisons: new Request('http://localhost:5000/datadiff/comparison',
      {
          mode: 'cors',
      }
    ),
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