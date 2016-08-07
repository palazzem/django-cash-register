import React from 'react';
import Paper from 'material-ui/Paper';
import Avatar from 'material-ui/Avatar';

import style from './ProductStyle.scss';


class ProductItem extends React.Component {
    render() {
        return (
            <Paper className={style.paper} zDepth={1}>
                <Avatar
                    className={style.avatar}
                    src={this.props.image}
                    size={100}
                />
                <p>{this.props.name}</p>
                <p>{this.props.price} &euro;</p>
            </Paper>
        );
    }
}

export default ProductItem;
