import React from 'react';
import ProductItem from './product/ProductItem';


class ProductList extends React.Component {
    processProduct(item) {
        return (
            <ProductItem
                key={item.id}
                name={item.name}
                price={item.price}
                image={item.image}
            />
        );
    }
    render() {
        var products = this.props.products.map(this.processProduct);
        return (
            <div>
                {products}
            </div>
        );
    }
}

export default ProductList;
