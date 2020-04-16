import React from 'react';

import {
    Typography,
    Box,
    TextField,
    Button,
    Tabs,
    Tab,
} from '@material-ui/core';

import MaterialTable from 'material-table';

import FileBrowser from 'react-keyed-file-browser'

import { Workbench } from './Layout';
import { getComparison } from './api'


function FileSelector() {
    return (
        <div>
            <Typography variant="h6">Select files to compare</Typography>
            <Typography color="text.secondary">
                Here you would make your selection of files to compare
            </Typography>
            <TextField label="file A" />
            <br />
            <TextField label="file B" />
            <br />
            <Button color="primary">Load files</Button>
        </div>
    );
}


function ComparedFileTabPanel(props) {
    const { children, value, index, ...other } = props;
    return (
        <div
            hidden={value !== index}
        >
            {value === index && <Box p={3}>{children}</Box>}
        </div>
    )
}

function ComparedFilesTabs(props) {
    const [value, setValue] = React.useState(0);
    const handleChange = (event, newValue) => {
        setValue(newValue);
    }

    const { component, data, labels } = props;

    return (
        <div>
            <Tabs value={value} onChange={handleChange}>
                <Tab label={`File A (${labels.A})`} />
                <Tab label={`File B (${labels.B})`} />
            </Tabs>
            <ComparedFileTabPanel value={value} index={0}>
                {component({ data: data.A })}
            </ComparedFileTabPanel>
            <ComparedFileTabPanel value={value} index={1}>
                {component({ data: data.B })}
            </ComparedFileTabPanel>
        </div>
    )

}

function FITSBrowser(props) {
    return (
        <MaterialTable
            columns={[
                { title: 'No', field: 'extension' },
                { title: 'Name', field: 'name' },
                { title: 'HDU Type', field: 'hdu_type' },
                { title: 'Dimensions', field: 'dimensions' },
                { title: 'Content Type', field: 'content_type' }
            ]}
            title="Which HDUs do you want to compare?"
            data={props.data}
            options={{
                selection: true
            }}
        />
    )
}

function TableFileBrowser({ data }) {

    const isParentPath = (maybeParent, path) => {
        console.log(`path=${path}`);
        console.log(`maybeParent=${maybeParent}`);

        const sep = '/';
        const getLastItem = (arr) => arr.slice(-1)[0];

        const basename = getLastItem(path.split(sep));
        const derivedPath = maybeParent + sep + basename;
        // console.log(`derivedPath=${derivedPath}`);

        const isParent = derivedPath === path;
        console.log(`isParent=${isParent}`);

        return isParent;
    };

    const [selRows, setSelRows] = React.useState([]);

    const handleSelRows = (selectedRows) => {
        if (selectedRows.length > 0) {
            selectedRows[0].tableData.checked = false;
        }
    }

    return (
        <MaterialTable
            columns={[
                { title: 'Path', field: 'path', editable: 'never' },
            ]}
            parentChildData={(row, rows) => rows.find(scannedRow => isParentPath(scannedRow.path, row.path))}
            data={data}
            options={{
                selection: true,
                selectionProps: rowData => ({
                    color: 'secondary',
                    // disabled: ! rowData.path.includes('.fits')
                    disabled: rowData.isDir,
                }),
                columnsButton: true,
                showSelectAllCheckbox: false,
                detailPanelType: 'single'
            }}
            onSelectionChange={(selectedRows) => handleSelRows(selectedRows)}
        />
    )
}

function KeyedFileBrowser({ data }) {
    // const classes = useStyles();
    return (
        <>
            {/* <CssBaseline /> */}
            <FileBrowser
                // className={classes.root}
                files={data}
            // icons={Icons.FontAwesome(4)}
            />
        </>
    )
}

function getComponent(type) {
    switch (type) {
        case "files":
            return TableFileBrowser;
        case "fits":
            return FITSBrowser;
        // TODO add fallback component (just show pretty-printed JSON?)
    }
}

function getWorkbenchItem(datum) {
    const getFallbackTitle = (str) => str.charAt(0).toUpperCase() + str.slice(1);
    const {type, ...otherProps} = datum;
    return {
        title: datum.title || getFallbackTitle(datum.type),
        component: getComponent(datum.type),
        props: otherProps,
    }
}

function getWorkbenchItems() {
    const data = getComparison();
    return (
        data
        .map(dataItem => getWorkbenchItem(dataItem))
        // .filter(item => item.component)
    );
}

export default function Compare() {
    return (
        <Workbench items={getWorkbenchItems()} />
    )
}
