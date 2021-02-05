import React, { useState, useEffect } from "react";

import { useForm } from "react-hooks-helper";

import { MainLayout } from './Layout';
import { WorkbenchContainer } from "./Workbench";
import { Sidebar } from './Sidebar';
import { Builder } from './Builder';


const BUILD_DATA = {
    dir: {
        A: '',
        B: '',
    },
    sample_file: '',
    fields: [],
    analysis_type: '',
    visualization_type: '',
    processing_status: null,
};

const COMPARISONS = [];


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

  useEffect( () => {
      fetch(requests.getComparisons)
      .then( (res) => res.json() )
      .then( (data) => {
          setComparisons(data);
      })
      .catch( (err) => {
          alert(JSON.stringify(err));
      })
  }, [completed]); 
  
  function runComparison() {
    const pendingComparison = {
      ...buildData,
      processing_status: pending
    };
    setPending([pendingComparison]);
    const req = new Request('http://localhost:5000/datadiff/comparison',
      {
        method: 'POST',
        mode: 'cors',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          ...buildData,
          paths: [
            buildData.dir.A,
            buildData.dir.B
          ],
        })
      }
    );

    fetch(req)
    .then( (res) => res.json() )
    .then( (data) => {
        setPending([]);
        setCompleted(completed + 1);
        setBuildData({});
    })
    .catch( (err) => {
        alert(JSON.stringify(err));
    })
  }

  return (
    <MainLayout>
      <WorkbenchContainer>
        <Builder formData={buildData} setFormData={setBuildData} dispatch={runComparison}/>
      </WorkbenchContainer>
      <Sidebar comparisons={comparisons} buildData={buildData} />
    </MainLayout>
  );
}