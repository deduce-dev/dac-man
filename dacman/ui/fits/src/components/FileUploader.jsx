import React from "react";
import { Typography, Container, Grid } from "@material-ui/core";
import Button from "@material-ui/core/Button";
import TextField from "@material-ui/core/TextField";
import Table from '@material-ui/core/Table';
import TableBody from '@material-ui/core/TableBody';
import TableCell from '@material-ui/core/TableCell';
import TableHead from '@material-ui/core/TableHead';
import TableRow from '@material-ui/core/TableRow';
import CloudUploadIcon from '@material-ui/icons/CloudUpload';

import { useStyles } from '../common/styles';
import { CSVVariableSelector } from './CSVVariableSelector';
import { VariableFlaggingDetails } from './VariableFlaggingDetails';
import { WorkbenchCard } from './WorkbenchCard';


function FileUploader({ stage, dispatch }) {
  const classes = useStyles();

  function createData(datetime, WindDir, Windspeed_ms, temp_f, dewp_f) {
    return { datetime, WindDir, Windspeed_ms, temp_f, dewp_f };
  }

  const rows = [
    createData('1/3/08 0:00', 330, 3.576, 81, 68),
    createData('1/3/08 1:00', 340, 1.341, 79, 68),
    createData('1/3/08 2:00', 'NA', 'NA', 'NA', 'NA'),
    createData('1/3/08 3:00', 'NA', 'NA', 'NA', 'NA'),
    createData('1/3/08 4:00', 'NA', 'NA', 'NA', 'NA'),
  ];

  return (
    <main className={classes.content}>
      <div className={classes.toolbar} />
      <Container maxWidth="lg" className={classes.container}>
        <Grid container spacing={3}>
          <WorkbenchCard
            key="card-initial"
            title="Choose File for flagging"
          >
            <TextField
              disabled
              fullWidth
              id="standard-disabled"
              defaultValue="4_NGEE/Powell/PNM_WS/AirportData_2008-2019_v3.csv"
              className={classes.textField}
              margin="normal"
            />
            <input
              accept="*.csv"
              className={classes.input}
              style={{ display: 'none' }}
              id="raised-button-file"
              type="file"
            />
            <br />
            <label htmlFor="raised-button-file">
              <Button
                variant="raised"
                component="span"
                className={classes.button}
                startIcon={<CloudUploadIcon />}
              >
                Upload File
              </Button>
            </label>
          </WorkbenchCard>
          <WorkbenchCard
            key="card-1"
            title="Preview"
          >
            <Table className={classes.table} aria-label="simple table">
              <TableHead>
                <TableRow>
                  <TableCell style={{ fontWeight: 'bold' }}>datetime</TableCell>
                  <TableCell align="right" style={{ fontWeight: 'bold' }}>WindDir</TableCell>
                  <TableCell align="right" style={{ fontWeight: 'bold' }}>Windspeed_ms</TableCell>
                  <TableCell align="right" style={{ fontWeight: 'bold' }}>TEMP_F</TableCell>
                  <TableCell align="right" style={{ fontWeight: 'bold' }}>DEWP_F</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {rows.map((row) => (
                  <TableRow key={row.datetime}>
                    <TableCell component="th" scope="row">
                      {row.datetime}
                    </TableCell>
                    <TableCell align="right">{row.WindDir}</TableCell>
                    <TableCell align="right">{row.Windspeed_ms}</TableCell>
                    <TableCell align="right">{row.temp_f}</TableCell>
                    <TableCell align="right">{row.dewp_f}</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            <Button
              variant="contained"
              color="primary"
            >
              Next
            </Button>
          </WorkbenchCard>
          <WorkbenchCard
            key="card-2"
          >
            <CSVVariableSelector />
            <Button
              variant="contained"
              color="primary"
            >
              Next
            </Button>
          </WorkbenchCard>
          <WorkbenchCard
            key="card-3"
            title="TEMP_F"
          >
            <VariableFlaggingDetails dispatch={dispatch} />
            <Button
              variant="contained"
              color="primary"
            >
              Next
            </Button>
          </WorkbenchCard>
          <WorkbenchCard
            key="card-4"
            title="Review Flagging Steps"
          >
            <Typography variant="h7" gutterBottom>
              Checking Null values for:
            </Typography>
            <Typography variant="h7" className={classes.paddedFormControl} gutterBottom>
              - TEMP_F
            </Typography>
            <Typography variant="h7" gutterBottom>
              Checking Duplicate values for:
            </Typography>
            <Typography variant="h7" className={classes.paddedFormControl} gutterBottom>
              - TEMP_F
            </Typography>
            <Button
              variant="contained"
              color="primary"
            >
              Run
            </Button>
          </WorkbenchCard>
        </Grid>
      </Container>
    </main>
  )
}

export {
  FileUploader
}
