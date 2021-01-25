import React from 'react';

import {
    Grid,
    Paper,
    Typography,
    Container
} from '@material-ui/core';

import { useStyles } from '../common/styles';
 
export function WorkbenchCard({ children, title }) {
    const classes = useStyles();
    return (
        <Grid item xs={12}>
            <Paper elevation={5} className={classes.paper}>
                <Typography variant="h6">
                    {title}
                </Typography>
                {children}
            </Paper>
            {/* <button variant="contained" color="primary" onclick={()=>console.log('this was clicked!')}>do something</button> */}
        </Grid>
    );
}

export function WorkbenchContainer({ children }) {
    const classes = useStyles();
    return (
        <main className={classes.content}>
            <div className={classes.toolbar} />
            <Container maxWidth="lg" className={classes.container}>
                {children}
            </Container>
        </main>
    );
}

 