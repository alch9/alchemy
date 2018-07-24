
import React from 'react';
import ReactDOM from 'react-dom';

import Modal from '@material-ui/core/Modal';
import Typography from '@material-ui/core/Typography';

function rand() {
    return Math.round(Math.random() * 20) - 10;
}

function getModalStyle() {
    const top = 50 + rand();
    const left = 50 + rand();
    
    return {
        top: `${top}%`,
        left: `${left}%`,
        transform: `translate(-${top}%, -${left}%)`,
    };
}

class Initial extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
        }
    }


    render() {
        return (
        <Modal open={true}>
            <div style={getModalStyle()}>
                <Typography variant="title" id="modal-title">
                    Text in a modal
                </Typography>
                <Typography variant="subheading" id="simple-modal-description">
                Duis mollis, est non commodo luctus, nisi erat porttitor ligula.
                </Typography>
            </div>
        </Modal>
        )
    }
}

module.exports = Initial;