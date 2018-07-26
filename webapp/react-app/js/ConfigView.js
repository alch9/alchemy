
import React from 'react';
import ReactDOM from 'react-dom';

import { Segment, Search, Grid, Button, Card, Table, Container } from 'semantic-ui-react';

class ConfigView extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            results: [],
            selectedUnit: null
        }

        this.handleSearchChange = this.handleSearchChange.bind(this)
        this.handleUnitClick = this.handleUnitClick.bind(this)
        this.getSelectedUnit = this.getSelectedUnit.bind(this)
        this.state.results = this.matchSource("")
    }

    matchSource(value) {
        var results = []
        for (var k in this.props.units) {
            if (k.indexOf(value) != -1) {
                results.push({title: k, description: k})
            }
        }

        return results
    }

    handleSearchChange(e, d) {
        var results = this.matchSource(d.value)
        this.setState({results: results})
    }

    handleUnitClick(e, d) {
        console.log("Unit button", d.uname)
        this.setState({selectedUnit: d.uname})
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
    }

    getSelectedUnit() {
        var ret = <div></div>
        if(!this.state.selectedUnit) {
            return ret
        }

        console.log("Unit Info props: ", this.props)
        var unit = this.props.units[this.state.selectedUnit]
        console.log('Selected unit', unit)
        var unit_type = this.getUnitType(unit)

        ret = (
            <Card>
                <Card.Content>
                    <Card.Header>
                        {this.state.selectedUnit}
                    </Card.Header>
                    <Card.Meta>{unit_type}</Card.Meta>
                    <Card.Description>
                        <pre>
                        {unit.desc}
                        </pre>
                    </Card.Description>
                </Card.Content>
            </Card>
        );

        return ret
    }

    render () {
        if(this.props.units == undefined) {
            return <div></div>
        }
        var ulist = []
        for (var i in this.state.results) {
            var title = this.state.results[i].title 
            ulist.push(<Button uname={title} key={title} onClick={this.handleUnitClick}>{title}</Button>)
        }

        var unitInfo = this.getSelectedUnit()
        return (
            <Grid>
                <Grid.Row>
                    <Search
                        minCharacters={2}
                        onSearchChange={this.handleSearchChange}
                        results={this.state.results}
                    />
                </Grid.Row>
                <Grid.Row columns={2}>
                    <Grid.Column>
                        <Button.Group vertical={true}>
                            {ulist}
                        </Button.Group>
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