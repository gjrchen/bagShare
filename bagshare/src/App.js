import './App.css';
import { useState } from 'react';
import Tabs from './Components/TabComponent/Tabs';
import logo from './Resources/HTG Logo.jpg';

const App = () => {
  return (
    <div className="App">
      <img src={logo} className="App-logo" alt="logo" />
      <Tabs/>
      <h1 className= "counter" > Bags Saved: <h2>{1324}</h2></h1>
    </div>
  );
}

export default App;
