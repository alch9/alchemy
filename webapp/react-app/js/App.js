import React from 'react';
import ReactDOM from 'react-dom';

import { Grid, Segment, Modal, Button, Menu, Container, GridColumn } from 'semantic-ui-react';

import ConfigSelect from './ConfigSelect';
import ConfigView from './ConfigView';

const title = 'Alchemy webapp';

const alchurl = 'http://localhost:5000'

export default class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            config: null,
            configOptions: null,
            units: null,
            flows: null,
            initial: false,
            configLoaded: false,
            activeMenuItem: "view-menu",
            version: null,
        }


        this.handleConfigChange = this.handleConfigChange.bind(this)
        this.fetchUnits = this.fetchUnits.bind(this)
        this.renderInitial = this.renderInitial.bind(this)
        this.handleClickModalAction = this.handleClickModalAction.bind(this)
        this.handleMenuClick = this.handleMenuClick.bind(this)
    }

    componentDidMount() {
        var _this = this

        console.log("cdm")
        window.fetch(alchurl + '/version')
        .then(function(response) {
            return response.json();
        })
        .then(function(j){
            _this.setState({version: j.version})
        });

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
            console.log("Units fetched for config", config)
            this.setState({config:config, units: j})
        });
    }

    fetchFlows(config) {
        window.fetch(alchurl + '/config/' + config + '/flows')
        .then(function(response) {
            return response.json();
        })
        .then(j => {
            this.setState({config:config, flows: j})
        });
    }

    handleConfigChange(e, d) {
        if (this.state.config == null) {
            console.log("config: ", d.value)
            this.fetchUnits(d.value)
        }else{
            if (this.state.config != d.value) {
                console.log("config: ", d.value)
                this.fetchUnits(d.value)
            }
        }
    }

    getMiddleRow() {
        if(this.state.config == null) {
            return (<Segment>Please select a configuration</Segment>)
        }else{
            return (
                <Grid.Column>
                    <ConfigView units={this.state.units}/> 
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

    handleMenuClick(e, {name}) {
        this.setState({activeMenuItem: name})
    }

    getMenu(options) {
        var menuitem = this.state.activeMenuItem
        return (
        <Menu color="black" borderless={true} size="large">
            <Menu.Item header>Alchemy {this.state.version} </Menu.Item>
            <Menu.Item><ConfigSelect options={options} onChange={this.handleConfigChange}/></Menu.Item>
            <Menu.Item 
                name='view-menu' 
                active={menuitem == 'view-menu'} 
                content='View'
                onClick={this.handleMenuClick}/>
            <Menu.Item 
                name='dev-menu' 
                content='Develop'
                active={menuitem == 'dev-menu'} 
                onClick={this.handleMenuClick}/>
        </Menu>
        )
    }

    render () {
        if (this.state.initial) {
            return this.renderInitial()
        }

        var mrow = this.getMiddleRow()
        var menu = this.getMenu(this.state.configOptions)
     
        return (
            <div>
                <Grid columns={1}>
                    <Grid.Column>
                        <Grid.Row>
                            {menu}
                        </Grid.Row>
                        <Grid.Row style={{padding: '30px', height:'80vh'}}>
                            {mrow}
                        </Grid.Row>
                        <Grid.Row>
                            <Segment>Message</Segment>
                        </Grid.Row>
                    </Grid.Column>
                </Grid>
            </div>
      );
    }
}
