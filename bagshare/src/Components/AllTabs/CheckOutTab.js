import React, { useEffect, useState } from "react";
import axios from "axios";

const CheckOutTab = () => {
    const [data, setdata] = useState({
        "ooga":"booga" 
    }, []);
    
    const fetchData = () => {
        axios.post("http://127.0.0.1:5000/api/get_account_info", {data})
              .then((response) => setdata(response.data));
      }
    
      useEffect(() => {
         fetchData();
      },[])
    
    return(
        
        <div className = "CheckOutTab">
            <p> Check out here</p>
            <p>{data.ooga}</p>
           
        </div>
    );

};

export default CheckOutTab;