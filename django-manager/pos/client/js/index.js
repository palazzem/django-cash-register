// Needed for onTouchTap
// http://stackoverflow.com/a/34015469/988941
import injectTapEventPlugin from 'react-tap-event-plugin';
injectTapEventPlugin();

import '../sass/main.scss';

import React from 'react';
import ReactDOM from 'react-dom';
import MuiThemeProvider from 'material-ui/styles/MuiThemeProvider';

import AppBarTop from './components/AppBar';
import ProductList from './components/ProductList';


const initialData = [
    {id: 1, name: 'Croissant', price: '5.90', image: 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Croissant,_cross_section.jpg'},
    {id: 2, name: 'Croissant', price: '5.90', image: 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Croissant,_cross_section.jpg'},
    {id: 3, name: 'Croissant', price: '5.90', image: 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Croissant,_cross_section.jpg'},
    {id: 4, name: 'Croissant', price: '5.90', image: 'https://upload.wikimedia.org/wikipedia/commons/9/9b/Croissant,_cross_section.jpg'},
];

const App = () => (
  <MuiThemeProvider>
    <div>
        <AppBarTop title='Dispensa 63 POS' />
        <ProductList products={initialData} />
    </div>
  </MuiThemeProvider>
);

ReactDOM.render(
  <App />,
  document.getElementById('app')
);
