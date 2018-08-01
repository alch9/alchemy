
import React from 'react';
import ReactDOM from 'react-dom';

import { Segment, List, Header, Grid, Card, Table, Divider, Input, Button } from 'semantic-ui-react';

class ConfigView extends React.Component {
    constructor(props) {
        super(props);

        var res = this.matchSource("", true)
        this.state = {
            unitResults: res.unitsResults,
            flowResults: res.flowResults,
            selectedUnit: null,
            selectedFlow: null,
            selectedItemType: null,
        }

        this.handleSearchChange = this.handleSearchChange.bind(this)
        this.handleUnitClick = this.handleUnitClick.bind(this)
        this.getSelectedItem = this.getSelectedItem.bind(this)
        this.renderUnitInput = this.renderUnitInput.bind(this)
        this.renderUnitOutput = this.renderUnitOutput.bind(this)
        this.renderUnitList = this.renderUnitList.bind(this)
        this.renderFlowList = this.renderFlowList.bind(this)
    }

    componentDidUpdate(prevProps) {
        if (this.props.configChangeCounter != prevProps.configChangeCounter) {
            var res = this.matchSource("", true)
            this.setState({
                unitResults: res.unitsResults, flowResults: res.flowResults,
            })
        }
    }

    matchSource(value, matchAll) {
        var unitResults = []
        for (var k in this.props.units) {
            var u = this.props.units[k]
            if (matchAll || k.toLowerCase().indexOf(value.toLowerCase()) != -1 
                || u.desc.toLowerCase().indexOf(value.toLowerCase()) != -1) {
                unitResults.push({title: k, description: u.desc})
            }
        }

        var flowResults = []
        for (var k in this.props.flows) {
            var f = this.props.flows[k]
            if (matchAll || k.toLowerCase().indexOf(value.toLowerCase()) != -1 
                || f.desc.toLowerCase().indexOf(value.toLowerCase()) != -1) {
                flowResults.push({title: k, description: f.desc})
            }
        }
        return {
            unitsResults: unitResults,
            flowResults: flowResults,
        }
    }

    handleSearchChange(e, d) {
        var results = this.matchSource(d.value, false)
        this.setState({unitResults: results.unitsResults, flowResults: results.flowResults})
    }

    handleUnitClick(e) {
        console.log("Unit item", e.target.name, "type", e.target.type)
        if(e.target.type == "unit") {
            this.setState({selectedUnit: e.target.name, selectedFlow: null, selectedItemType: e.target.type})
        }else{
            this.setState({selectedUnit: null, selectedFlow: e.target.name, selectedItemType: e.target.type})
        }
    }

    getUnitType(unit) {
        var type = unit['type']
        if (type == 1) {
            return 'Simple'
        }
        if (type == 2) {
            return 'Meta'
        }
        if (type == 3) {
            return 'Derived'
        }
        if (type == 4) {
            return 'Simple wrap'
        }
    }

    renderUnitInput(unit) {
        var input_el = []
        for (var arg in unit.input) {
            var defval = <div></div>;
            if('def' in unit.input[arg]) {
                defval = unit.input[arg].def
                if (typeof defval == "string" && defval.length == 0) {
                    defval = "<empty string>"
                }
            }
            var j = (<Table.Row key={unit.name + "." + arg}>
                <Table.Cell>
                    {arg}
                </Table.Cell>
                <Table.Cell>
                    {defval}
                </Table.Cell>
                <Table.Cell>
                    {unit.input[arg].desc}
                </Table.Cell>
                </Table.Row>)
            
            input_el.push(j)
        }

        return (
            <div>
            <Header as='h4' attached='top'>
                Input
            </Header>
            <Table celled striped attached size="small">
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>Argument</Table.HeaderCell>
                        <Table.HeaderCell>Default value</Table.HeaderCell>
                        <Table.HeaderCell>Description</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {input_el}
                </Table.Body>
            </Table>
            </div>)
    }

    renderUnitOutput(unit) {
        var output_el = []
        for (var arg in unit.output) {
            var j = (<Table.Row key={unit.name + "." + arg}>
                <Table.Cell>
                    {arg}
                </Table.Cell>
                <Table.Cell>
                    {unit.output[arg]}
                </Table.Cell>
                </Table.Row>)
            
            output_el.push(j)
        }

        return (
            <div>
            <Header as='h4' attached='top'>
                Output
            </Header>
            <Table celled striped attached size="small">
                <Table.Header>
                    <Table.Row>
                        <Table.HeaderCell>Variable</Table.HeaderCell>
                        <Table.HeaderCell>Description</Table.HeaderCell>
                    </Table.Row>
                </Table.Header>
                <Table.Body>
                    {output_el}
                </Table.Body>
            </Table>
            </div>)

    }

    getSelectedItem() {
        var input_content = []
        var output_content = []
        var header = ""
        var meta = ""
        var desc = ""
        var renderItem = false

        if (this.state.selectedUnit) {
            if ( !(this.state.selectedUnit in this.props.units)) {
                return <div></div>
            }

            console.log("Unit Info props: ", this.props)
            var unit = this.props.units[this.state.selectedUnit]
            console.log('Selected unit', unit)
            var unit_type = this.getUnitType(unit)

            header = this.state.selectedUnit
            meta = "Unit: " + unit_type
            input_content = this.renderUnitInput(unit)
            output_content = this.renderUnitOutput(unit)
            desc = unit.desc
            renderItem = true
        }

        if (this.state.selectedFlow) {
            if ( !(this.state.selectedFlow in this.props.flows)) {
                return <div></div>
            }

            var flow = this.props.flows[this.state.selectedFlow]

            header = this.state.selectedFlow
            meta = "Flow"
            input_content = this.renderUnitInput(flow)
            output_content = this.renderUnitOutput(flow)
            desc = flow.desc
            renderItem = true
        }

        var ret = <div></div>
        if(renderItem) {
            ret = (
            <Card fluid>
                <Card.Content>
                    <Card.Header>
                        {header}
                    </Card.Header>
                    <Card.Meta>{meta}</Card.Meta>
                    <Card.Description>
                        <Segment basic style={{background: '#f9f7e5'}}>
                        <pre>
                        {desc}
                        </pre>
                        </Segment>
                    </Card.Description>
                    <Divider/>
                    {input_content}
                    <Divider/>
                    {output_content}
                </Card.Content>
            </Card>
        );
        }

        return ret
    }

    renderUnitList() {
        var ulist = []
        for (var i in this.state.unitResults) {
            var title = this.state.unitResults[i].title 
            var desc = this.state.unitResults[i].description
            desc = desc.split("\n")[0]
            ulist.push(
                <List.Item key={title}>
                    <List.Content>
                    <a href="#" type="unit" name={title} onClick={this.handleUnitClick}>{title}</a>
                    </List.Content>
                    <List.Description>
                        {desc}
                    </List.Description>
                </List.Item>)
        }

        return (<List relaxed style={{overflow: "auto"}}>
            {ulist}
        </List>)
    }

    renderFlowList() {
        var flist = []
        for (var i in this.state.flowResults) {
            var title = this.state.flowResults[i].title 
            var desc = this.state.flowResults[i].description
            desc = desc.split("\n")[0]
            flist.push(
                <List.Item key={title}>
                    <List.Content>
                    <a href="#" type="flow" name={title} onClick={this.handleUnitClick}>{title}</a>
                    </List.Content>
                    <List.Description>
                        {desc}
                    </List.Description>
                </List.Item>)
        }

        return (<List relaxed>{flist}</List>)
    }

    render () {
        if(this.props.units == undefined || this.props.flows == undefined) {
            return <div></div>
        }
        var ulist = this.renderUnitList()
        var flist = this.renderFlowList()
        var unitInfo = this.getSelectedItem()
        return (
            <Grid>
                <Grid.Row>
                    <Input
                        icon='search'
                        placeholder='Search ...'
                        onChange={this.handleSearchChange}
                    />
                </Grid.Row>
                <Grid.Row columns={2} divided>
                    <Grid.Column width={3}>
                            <Header as='h5' content='Units'/>
                            <Divider/>
                            {ulist}
                    </Grid.Column>
                    <Grid.Column width={3}>
                            <Header as='h5' content='Flows'/>
                            <Divider/>
                            {flist}
                    </Grid.Column>
                    <Grid.Column>
                        {unitInfo}
                    </Grid.Column>
                </Grid.Row>
            </Grid>
        );
    }
}

module.exports = ConfigView;
