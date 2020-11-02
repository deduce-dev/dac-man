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

import { useParams } from "react-router-dom";

import { Workbench } from './Layout';
import { 
    getCommonLayers,
} from './api'


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

function ComparedTabPanel(props) {
    const { children, value, index, ...other } = props;
    return (
        <div
            hidden={value !== index}
        >
            <Box p={3}>{children}</Box>
        </div>
    )
}

function ComparedFilesTabs(props) {
    const [value, setValue] = React.useState(0);
    const handleChange = (event, newValue) => {
        setValue(newValue);
    }

    const { component, files, labels } = props;

    return (
        <div>
            <Tabs value={value} onChange={handleChange}>
                <Tab label={`File A (${labels.A})`} />
                <Tab label={`File B (${labels.B})`} />
            </Tabs>
            <ComparedFileTabPanel value={value} index={0}>
                {component({ files: files.A })}
            </ComparedFileTabPanel>
            <ComparedFileTabPanel value={value} index={1}>
                {component({ files: files.B })}
            </ComparedFileTabPanel>
        </div>
    )

}

function TabbedCompareWrapper() {

}

function TabbedCompareDirContents({contents, labels}) {
    const [value, setValue] = React.useState(0);
    const handleChange = (event, newValue) => {
        setValue(newValue);
    }

    let component = TableFileBrowser;
    return (
        <div>
            <Tabs value={value} onChange={handleChange}>
                <Tab label={`File A (${labels.A})`} />
                <Tab label={`File B (${labels.B})`} />
            </Tabs>
            {/* <ComparedFileTabPanel value={value} index={0}>
                {component({ files: contents.A })}
            </ComparedFileTabPanel>
            <ComparedFileTabPanel value={value} index={1}>
                {component({ files: contents.B })}
            </ComparedFileTabPanel> */}
            <Box p={3} hidden={value === 0}>{component({ files: contents.A })}</Box>
            <Box p={3} hidden={value === 1}>{component({ files: contents.B })}</Box>
        </div>
    )
}

function MakeGenericTabbedCompare(component) {
    function TabbedCompare({contents, labels}) {
        console.log('Inside TabbedCompare')
        console.log('Component:'); console.log(component);
        const [shownIdx, setShownIdx] = React.useState(0);
        const handleChange = (event, newValue) => {
            setShownIdx(newValue);
        };
        labels = labels || {A: "A", B: "B"};
        return (
            <div>
                <Tabs value={shownIdx} onChange={handleChange}>
                    <Tab label={`File A (${labels.A})`} />
                    <Tab label={`File B (${labels.B})`} />
                </Tabs>
                <ComparedFileTabPanel value={shownIdx} index={0}>
                    {component({ contents: contents.A })}
                </ComparedFileTabPanel>
                <ComparedFileTabPanel value={shownIdx} index={1}>
                    {component({ contents: contents.B })}
                </ComparedFileTabPanel>
                {/* <div hidden={value === 0}>
                    <Box p={3}>{component({ contents: contents.A })}</Box>
                </div>
                <div hidden={value === 1}>
                    <Box p={3}>{component({ contents: contents.B })}</Box>
                </div> */}
                {/* <ComparedTabPanel value={value} index={0}>
                    {component({ contents: contents.A })}
                </ComparedTabPanel>
                <ComparedTabPanel value={value} index={1}>
                    {component({ contents: contents.B })}
                </ComparedTabPanel> */}
                {/* {shownIdx === 0 && <Box p={3}>{component({ contents: contents.A })}</Box>}
                {shownIdx === 1 && <Box p={3}>{component({ contents: contents.B })}</Box>} */}
            </div>
        )
    }

    console.log('About to return TabbedCompare closure');

    return TabbedCompare;
}

function MakeGenericSimpleCompare(component) {
    function SimpleCompare({contents, labels, ...layerData}) {
        console.log('Inside SimpleCompare')
        console.log('Component:'); console.log(component);

        labels = labels || {A: "A", B: "B"};
        return (
            <div>
                <Box p={3} >
                    {component({ contents: contents.A })}
                </Box>
                <Box p={3} >
                    {component({ contents: contents.B })}
                </Box>
            </div>
        )
    };
    return SimpleCompare;
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
            data={props.contents}
            options={{
                selection: true
            }}
        />
    )
}

function TableFileBrowser({ contents }) {

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

    // const [selRows, setSelRows] = React.useState([]);

    // const handleSelRows = (selectedRows) => {
    //     if (selectedRows.length > 0) {
    //         selectedRows[0].tableData.checked = false;
    //     }
    // }

    console.log('TableFileBrowser: ');
    console.log('files:'); console.log(contents);

    return (
        <MaterialTable
            columns={[
                { title: 'Path', field: 'path', editable: 'never' },
            ]}
            // parentChildData={(row, rows) => rows.find(scannedRow => isParentPath(scannedRow.path, row.path))}
            data={contents}
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
            // onSelectionChange={(selectedRows) => handleSelRows(selectedRows)}
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

function getWorkbenchComponent({type, ...rest}) {
    let wrapper = MakeGenericSimpleCompare;
    console.log(`Checking type: ${type}`)
    switch (type) {
        case "dir":
            console.log('Found a "dir" component!')
            return wrapper(TableFileBrowser);
        case "fits":
            console.log('Found a "fits" component!')
            return wrapper(FITSBrowser);
    }
}

export default function Compare({comparison}) {
    // let cid = useParams().cid;
    // console.log('cid:')
    // console.log(cid)
    let layers = getCommonLayers();
    // let layers = [];
    console.log('[Compare]')
    console.log('layers:')
    console.log(layers)

    layers = [...layers, ...comparison.layers || []];
    console.log('These are the layers after concat:')
    console.log(layers);
    return (
        <Workbench items={layers} getComponent={getWorkbenchComponent} />
        // <Workbench items={getWorkbenchItemsFromLayer(comparison)} />
    )
}

