
import React from 'react';
import ReactDOM from 'react-dom';

import { Header, Segment, Dropdown } from 'semantic-ui-react';

class ConfigSelect extends React.Component {
    constructor(props) {
        super(props);
    }

    render () {
        return (
            <Dropdown 
                placeholder="Select config" 
                fluid 
                search 
                selection 
                defaultValue={this.props.defaultValue}
                onChange={this.props.onChange}
                options={this.props.options}
                />
        );
    }
}

module.exports = ConfigSelect;