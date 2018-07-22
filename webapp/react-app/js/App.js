import React from 'react';
import ReactDOM from 'react-dom';

import { Grid, Segment, Modal, Button } from 'semantic-ui-react';

import ConfigSelect from './ConfigSelect';
import ConfigContent from './ConfigContent';

const title = 'Alchemy webapp';

const alchurl = 'http://localhost:5000'

export default class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            config: null,
            configOptions: null,
            units: null,
            initial: false,
            configLoaded: false,
        }


        this.handleConfigChange = this.handleConfigChange.bind(this)
        this.fetchUnits = this.fetchUnits.bind(this)
        this.renderInitial = this.renderInitial.bind(this)
        this.handleClickModalAction = this.handleClickModalAction.bind(this)
    }

    componentDidMount() {
        var _this = this

        console.log("cdm")
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

    fetchUnits(config) {
        window.fetch(alchurl + '/config/' + config + '/units')
        .then(function(response) {
            return response.json();
        })
        .then(j => {
            this.setState({units: j})
        });
    }

    handleConfigChange(e, d) {
        if (this.state.config == null) {
            console.log("config: ", d.value)
            this.setState({config: d.value, units: units})
            var units = this.fetchUnits(d.value)
        }else{
            if (this.state.config != d.value) {
                console.log("config: ", d.value)
                this.setState({config: d.value, units: units})
                var units = this.fetchUnits(d.value)
            }
        }
    }

    getMiddleRow() {
        if(this.state.config == null) {
            return (<Segment>Please select a configuration</Segment>)
        }else{
            return (
                <Grid.Column>
                    <ConfigContent units={this.state.units}/> 
                </Grid.Column>
            )
        }
    }

    handleClickModalAction(d) {
        console.log("modal click", d.value, this.state.config)
        if( this.state.config != null) {
            this.setState({initial: false})
        }
    }

    renderInitial() {
        var defaultValue = null
        var options = this.state.configOptions;
        if (options != null && options.length > 0) {
            defaultValue = options[0].text
        }
        console.log("def", defaultValue)
        return (
            <div>
                <Modal open={this.state.initial}>
                    <Modal.Header>Select Alchemy configuration</Modal.Header>
                    <Modal.Content>
                        <ConfigSelect 
                            onChange={this.handleConfigChange}
                            options={this.state.configOptions}
                            defaultValue={defaultValue}
                        />
                    </Modal.Content>
                    <Modal.Actions>
                        <Button onClick={this.handleClickModalAction}>Ok</Button>
                    </Modal.Actions>
                </Modal>
            </div>
        )
    }

    render () {

        if (this.state.initial) {
            return this.renderInitial()
        }

        var mrow = this.getMiddleRow()
     
        return (
            <div>
                <Grid>
                    <Grid.Row stretched={true} columns={2}>
                        <Grid.Column stretched={true} width={2}>
                            <Segment basic={true} inverted={true} textAlign="center">Alchemy</Segment>
                        </Grid.Column>
                        <Grid.Column stretched={true} width={2}>
                            <ConfigSelect 
                                onChange={this.handleConfigChange} 
                                options={this.state.configOptions}
                                defaultValue={this.state.config}
                            />
                        </Grid.Column>
                    </Grid.Row>
                    <Grid.Row stretched={true} columns={1}>
                        {mrow}
                    </Grid.Row>
                    <Grid.Row stretched={true}>
                        <Grid.Column stretched={true}>
                            <Segment>Bottom Row</Segment>
                        </Grid.Column>
                    </Grid.Row>
                </Grid>
            </div>
      );
    }
}
