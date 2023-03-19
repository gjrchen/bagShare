import './App.css';
import { useEffect, useState } from 'react';
import Tabs from './Components/TabComponent/Tabs';
import logo from './Resources/HTG Logo.jpg';
import axios from 'axios';


const App = () => {
  const [counter, setcounter] = useState(1232)
  const update_funct = () => {
    axios.get("http://127.0.0.1:5000/api/counter_update" )
    .then((response) => {
      setcounter(Number(response.data))  
      return null
    })
  }
  
  update_funct()

  return (
    <div className="App">
      <img src={logo} className="App-logo" alt="logo" />
      <Tabs/>
      <h1 className= "counter" > Bags Saved: <h2>{counter}</h2></h1>
    </div>
  );
}

export default App;
