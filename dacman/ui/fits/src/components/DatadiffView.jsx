import React from "react";

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
};

const COMPARISONS = [];


export function DatadiffView() {
  const [buildData, setBuildData] = useForm(BUILD_DATA);
  return (
    <MainLayout>
      <WorkbenchContainer>
        <Builder formData={buildData} setFormData={setBuildData} />
      </WorkbenchContainer>
      <Sidebar comparisons={COMPARISONS} buildData={buildData} />
    </MainLayout>
  );
}