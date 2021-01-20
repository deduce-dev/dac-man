import React, { useCallback } from "react";
import { Typography, Container, Grid } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import Card from '@material-ui/core/Card';
import TextField from "@material-ui/core/TextField";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';
import { useDropzone } from 'react-dropzone';

import { useStyles } from '../common/styles';
import { CSVVariableSelector } from './CSVVariableSelector';
import { VariableFlaggingDetails } from './VariableFlaggingDetails';
import { WorkbenchCard } from './WorkbenchCard';

import axios from 'axios';

import styled from 'styled-components';


const getColor = (props) => {
  if (props.isDragAccept) {
      return '#00e676';
  }
  if (props.isDragReject) {
      return '#ff1744';
  }
  if (props.isDragActive) {
      return '#2196f3';
  }
  return '#eeeeee';
}

const FileUploaderContainer = styled.div`
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  border-width: 2px;
  border-radius: 2px;
  border-color: ${props => getColor(props)};
  border-style: dashed;
  background-color: #fafafa;
  color: #bdbdbd;
  outline: none;
  transition: border .24s ease-in-out;
`;

function FileUploader({ dispatch }) {
  const classes = useStyles();

  function createData(id, datetime, WindDir, Windspeed_ms, TEMP_F, DEWP_F) {
    return {id, datetime, WindDir, Windspeed_ms, TEMP_F, DEWP_F};
  }

  /*
  function createData(id, datetime, WindDir, Windspeed_ms, TEMP_F, DEWP_F) {
    return {id, datetime, WindDir, Windspeed_ms, TEMP_F, DEWP_F };
  }

  let dataReview = {
    show: true,
    columns: [
      { field: 'id', headerName: 'ID', width: 70 },
      { field: 'datetime', headerName: 'datetime', width: 130 },
      { field: 'WindDir', headerName: 'WindDir', width: 90 },
      { field: 'Windspeed_ms', headerName: 'Windspeed_ms', width: 90},
      { field: 'TEMP_F', headerName: 'TEMP_F', width: 90 },
      { field: 'DEWP_F', headerName: 'DEWP_F', width: 90 },
    ],
    rows: [
      createData(1, '1/3/08 0:00', 330, 3.576, 81, 68),
      createData(2, '1/3/08 1:00', 340, 1.341, 79, 68),
      createData(3, '1/3/08 2:00', 'NA', 'NA', 'NA', 'NA'),
      createData(4, '1/3/08 3:00', 'NA', 'NA', 'NA', 'NA'),
      createData(5, '1/3/08 4:00', 'NA', 'NA', 'NA', 'NA'),
    ],
    datasetVarsTemplate: [
      { title: 'Variables', field: 'varName' },
      { title: 'Content Type', field: 'contentType' }
    ],
    datasetVars: [
      {
        varName: 'datetime',
        contentType: 'String'
      },
      {
        varName: 'WindDir',
        contentType: 'Integer'
      },
      {
        varName: 'Windspeed_ms',
        contentType: 'Float'
      },
      {
        varName: 'TEMP_F',
        contentType: 'Integer'
      },
      {
        varName: 'DEWP_F',
        contentType: 'Integer'
      },
    ]
  }
  */

  let dataReview = {
    show: true,
    datasetVarsTemplate: [
      { title: 'Variables', field: 'varName' },
      { title: 'Content Type', field: 'contentType' }
    ]
  }

  const uploadFile = (project_id, data) => {
    return {
      type: 'UPLOAD_FILE',
      payload: {
        project_id: project_id,
        data: data
      }
    };
  }

  /*const onDrop = useCallback(acceptedFiles => {
    // Do something with the files
    dispatch(uploadFile());
  }, []) */

  const {
    acceptedFiles,
    fileRejections,
    getRootProps,
    getInputProps,
    isDragActive,
    isDragAccept,
    isDragReject
  } = useDropzone({ 
    maxFiles:1,
    accept: '.csv',
    onDropAccepted: (files) => {
      var dataset = files[0]
      var formData = new FormData();
      formData.append("upload_dataset", dataset);
      axios.post('/flagging/upload', formData, {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
      })
      .then((response) => {
        //console.log(response.data);
        //var resData = JSON.parse(JSON.stringify(response.data));
        //var resData = JSON.parse(response.data);
        var resData = response.data

        dataReview = {
          ...dataReview,
          ...resData.data,
          dataset_name: dataset.name
        }

        //console.log(resData);
        console.log(dataReview)
        dispatch(uploadFile(resData.project_id, dataReview));
      })
      .catch((error) => {
        console.log(error);
      });
    }
  });

  const acceptedFileItems = acceptedFiles.map(file => (
    <li key={file.path}>
      {file.path} - {file.size} bytes
    </li>
  ));

  return (
    <WorkbenchCard
      key="card-initial"
      title="Choose File for flagging"
    >
      <div className="container">
        <FileUploaderContainer {...getRootProps({isDragActive, isDragAccept, isDragReject})}>
            <input {...getInputProps()} />
            <p>Drag & drop a file here, or click to select files</p>
            <em>(Only 1 file can be dropped here)</em>
        </FileUploaderContainer>
      </div>
      { acceptedFileItems.length > 0 && (
        <aside>
          <h4>File</h4>
          <ul>{acceptedFileItems}</ul>
        </aside>
      )}
    </WorkbenchCard>
  )
}

export {
  FileUploader
}
