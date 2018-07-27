
import React from 'react';
import ReactDOM from 'react-dom';

import { Tab } from 'semantic-ui-react';

import UnitInfo from './UnitInfo';

class ConfigContent extends React.Component {
    constructor(props) {
        super(props);
    }



    render() {
        var panes = [
            { menuItem: 'Units', render: () => <Tab.Pane><UnitInfo units={this.props.units}/></Tab.Pane> },
            { menuItem: 'Flows', render: () => <Tab.Pane>Tab 2 Content</Tab.Pane> },
            { menuItem: 'Run', render: () => <Tab.Pane>Tab 3 Content</Tab.Pane> }
        ]
        return (
            <Tab panes={panes}/>
        );
    }
}

module.exports = ConfigContent;