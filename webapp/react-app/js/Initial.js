
import React from 'react';
import ReactDOM from 'react-dom';

import { Header, Sidebar, Segment, Dropdown, Divider, SidebarPushable } from 'semantic-ui-react';

class Initial extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
          visible: true,
        };
    }

    handleButtonClick() {
        this.setState({ visible: !this.state.visible })
    }
    handleSidebarHide() {
        this.setState({ visible: false })
    }

    render () {
        return (
            <Segment>
            <Header size='tiny'>Configuration</Header>
            <Dropdown 
                placeholder="Select config" 
                fluid 
                search 
                selection 
                defaultValue={0}
                options={
                    [
                        {text: "alchemy", value: "alchemy"},
                        {text: "alchemy-std", value: "alchemy-std"},
                        {text: "phoenix_units", value: "phoenix_units"}
                    ]
                }/>
            </Segment>
        );
    }
}

module.exports = Initial;