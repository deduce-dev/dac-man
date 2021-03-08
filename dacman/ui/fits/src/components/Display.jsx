import React from 'react';
import { Link as RouterLink } from 'react-router-dom';

import {
    Typography,
    List,
    ListItem,
    ListItemText,
    Chip,
    Tooltip,
    Paper,
    Button,
    LinearProgress,
} from "@material-ui/core";

import { WorkbenchCard } from "./WorkbenchCard";
import { useStyles } from "../common/styles";


function prettyTimestamp(ts) {
    return new Date(ts).toLocaleString();
}

export function Timestamp({ts, label = ""}) {
    return (
        <i>   {label ? `${label}: ` : ""}{prettyTimestamp(ts)}</i>
    )
}

export function PrettyUID({uid}) {
    const abbrev = (uid || "").slice(0, 8);
    return (
        <Tooltip title={uid}>
            <strong>
                <kbd>{abbrev}</kbd>
            </strong>
        </Tooltip>
    )
}

export function Loading() {
  return (
    <WorkbenchCard>
        <Typography variant="h4" align="center">
            Loading...
        </Typography>
        <LinearProgress/>
    </WorkbenchCard>
  );
}

export function DatasetInlineReference({resource_key, maxLen = 32}) {
    const toDisplay = resource_key.slice(0, maxLen);
    // const url = `/datadiff/contents/datasets/${resource_key}`;
    return (
        <>
            <strong><kbd>{toDisplay}</kbd></strong>
        </>
    )
}

export function ResourceDisplay({ resource_key, label, created_at, maxLen = 32, ...other }) {
    label = label || (resource_key || "").slice(0, maxLen);
    return (
        <Typography>
            <strong><kbd>{label}</kbd></strong>
            {
                created_at && (
                    <i>    Created at: {prettyTimestamp(created_at)}</i>
                )
            }
        </Typography>
    )
}

export function ComparisonSummary({ resource_key, options, base = {}, new: new_ = {}, completed_at }) {
    return (
        <>
            <Typography display="inline" variant="h6">
                <DatasetInlineReference {...base}/> ➔ <DatasetInlineReference {...new_}/>
                {/* <PrettyUID uid={options.base}/> ➔ <PrettyUID uid={options.new}/> */}
            </Typography>
            <Typography>
                Comparison <PrettyUID uid={resource_key}/><Timestamp ts={completed_at} label="Completed at"/>
            </Typography>
        </>
    );
}

export function ComparisonDetail({ options }) {
    const FIELD_COLORS = {
        0: "#4c78a8",
        1: "#f58518",
        2: "#e45756",
        3: "#72b7b2",
        4: "#54a24b",
        5: "#eeca3b",
        6: "#b279a2",
        7: "#ff9da6",
        8: "#9d755d",
        9: "#bab8ac",
    };
    const { fields } = options;
    console.log(fields);
    return (
        <div>
            <List dense>
                {fields.map((f, idx) => {
                    return (
                        <ListItem key={f}>
                            {/* <Typography><kbd>{f}</kbd></Typography> */}
                            <Chip label={f} style={{backgroundColor: FIELD_COLORS[idx]}}/>
                        </ListItem>
                    );
                })}
            </List>
        </div>
    )
}

export function SubmittedComparison({ base, new: new_, resource_key, completed_at }) {
    const classes = useStyles();
    return (
        <Paper elevation={5} className={classes.paper}>
            <Typography display="inline" variant="h5">
                <DatasetInlineReference {...base}/> ➔ <DatasetInlineReference {...new_}/>
            </Typography>
            <Typography>
                Comparison <PrettyUID uid={resource_key}/><Timestamp ts={completed_at} label="Completed at"/>
            </Typography>
            <Button color="primary" component={RouterLink} to={`/datadiff/comparisons/${resource_key}/results`}>Browse Results</Button>
        </Paper>
    )
}