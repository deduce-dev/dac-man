import React, { useReducer } from "react";
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

import './css/components.scss';


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

const init = (file_list) => {
  return { uploaded: Array.from(file_list, x => false) }
};

function reducer(state, action) {
  switch (action.type) {
    case 'CHOSE_FILES_TO_UPLOAD':
      return {
        ...state,
        files: action.payload,
        uploaded: Array.from(action.payload, x => false)
      };
    case 'UPLOADED_FILE':
      var new_uploaded = state.uploaded;
      new_uploaded[action.payload] = true;
      return {
        ...state,
        uploaded: new_uploaded
      };
    default:
      return state;
  }
}



function FileUploader({ parentDispatch, file_list }) {
  const classes = useStyles();

  const [state, dispatch] = useReducer(reducer, file_list, init);

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

  const choseFilesToUpload = (files) => {
    return {
      type: 'CHOSE_FILES_TO_UPLOAD',
      payload: files
    };
  }

  const uploadedFile = (index) => {
    return {
      type: 'UPLOADED_FILE',
      payload: index
    };
  }

  const loadSample = (project_id, data) => {
    return {
      type: 'LOAD_SAMPLE',
      payload: {
        project_id: project_id,
        data: data
      }
    };
  }

  const formatBytes = (bytes, decimals = 2) => {
    if (bytes === 0) return '0 Bytes';

    const k = 1024;
    const dm = decimals < 0 ? 0 : decimals;
    const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

    const i = Math.floor(Math.log(bytes) / Math.log(k));

    return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
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
    maxFiles: 0,
    accept: '.csv',
    onDropAccepted: (files) => {
      parentDispatch(choseFilesToUpload(files));

      console.log("Accepted Files")

      let upload_start = async () => {
        let project_id_req = await axios.get('/flagging/id');

        let project_id = project_id_req.data.project_id;
        console.log("project_id");
        console.log(project_id);

        for (var i = 0; i < files.length; i++) {
          var dataset = files[i];
          var formData = new FormData();
          formData.append("upload_dataset", dataset);

          let req = axios.post('/flagging/upload/' + project_id + '/' + i,
            formData, {
              headers: {
                'Content-Type': 'multipart/form-data'
              }
            }
          );

          var resData = null;
          req.then((response) => {
            dispatch(uploadedFile(response.data.file_index));
            //console.log(response.data);
            //var resData = JSON.parse(JSON.stringify(response.data));
            //var resData = JSON.parse(response.data);

            if (resData === null) {
              resData = response.data;

              dataReview = {
                ...dataReview,
                ...resData.data,
                dataset_name: dataset.name,
                dataset_shape: [...resData.data_total_shape]
              }

              console.log(resData);
              console.log(dataReview);

              parentDispatch(
                loadSample(
                  resData.project_id,
                  dataReview
                )
              );
            }
          })
          .catch((error) => {
            console.log(error);
          });
        }
      }
      upload_start()
      .then(res => console.log(res))
      .catch((error) => {
        console.log(error);
      });
    }
  });

  const styled_file_list = file_list.map((file, i) => (
    <li key={file.path} className={classes.uploadFileList}>
    <Grid container spacing={3}>
      <Grid item xs={8}>
        <div>{file.path}</div>
      </Grid>
      <Grid item xs={1}>
        { state.uploaded[i] ? (
            <div className={classes.uploadedBG}><span>Uploaded</span></div>
          ) : (
            <div className={"uploading"}>uploading<span>.</span><span>.</span><span>.</span></div>
          )
        }
      </Grid>
      <Grid item xs={2}>
        <div style={{marginLeft: "1em"}}>{formatBytes(file.size)}</div>
      </Grid>
    </Grid>
    </li>
  ));

  return (
    <WorkbenchCard
      key="card-initial"
      title="Upload Files for Flagging"
    >
      <div className="container">
        <FileUploaderContainer {...getRootProps({isDragActive, isDragAccept, isDragReject})}>
            <input {...getInputProps()} />
            <p>Drag & drop files here, or click to select files</p>
            <em>(Only .csv files are supported)</em>
        </FileUploaderContainer>
      </div>
      { styled_file_list.length > 0 && (
        <aside>
          <h4>Files</h4>
          <ul>{styled_file_list}</ul>
        </aside>
      )}
    </WorkbenchCard>
  )
}

export {
  FileUploader,
  FileUploaderContainer
}
