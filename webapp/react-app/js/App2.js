import React from 'react';
import ReactDOM from 'react-dom';

import Grid from '@material-ui/core/Grid';
import Modal from '@material-ui/core/Modal';
import Initial from './Initial';

const title = 'Alchemy webapp';

const alchurl = 'http://localhost:5000'

export default class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            configOptions: null,
            config: null,
            configLoaded: false,
            initial: true,
        }

        this.renderInitial = this.renderInitial.bind(this)
    }

    componentDidMount() {
        var _this = this

        var options = []
        window.fetch(alchurl + '/config')
        .then(function(response) {
            return response.json();
        })
        .then(function(j){
            for (var k in j) {
                options.push({text: k, value: k})
            }
            _this.setState({configOptions: options, configLoaded: true})
        });
    }

    renderInitial() {
        return (
            <Initial/>
        )
    }

    render () {
        if (this.state.initial) {
            return this.renderInitial()
        }
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
