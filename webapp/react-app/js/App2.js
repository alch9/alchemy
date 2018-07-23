import React from 'react';
import ReactDOM from 'react-dom';

import Grid from '@material-ui/core/Grid';

const title = 'Alchemy webapp';

const alchurl = 'http://localhost:5000'

export default class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        }
    }

    render () {
        return (
            <Grid container spacing={0}>
                <Grid item xs={3}>
                    <div>1</div>
                </Grid>
                <Grid item xs={3}>
                    <div>1</div>
                </Grid>
            </Grid>
        )
    }
}
