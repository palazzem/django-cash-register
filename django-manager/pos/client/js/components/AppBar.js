import React from 'react';
import AppBar from 'material-ui/AppBar';
import FlatButton from 'material-ui/FlatButton';


class AppBarTop extends React.Component {
    render() {
        return (
            <AppBar
              title={this.props.title}
              iconElementRight={<FlatButton onClick={this.handlePrintReceipt} label='Print Receipt' />}
            />
        );
    }

    handlePrintReceipt() {
        alert('NotImplementedError');
    }
}

export default AppBarTop;
