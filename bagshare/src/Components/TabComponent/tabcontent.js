import React from "react";
 
const TabContent = ({id, activeTab, children}) => {
  /*useEffect( () => {
    fetch ("http://127.0.0.1:5000/api/get_account_info").then((res) =>
    res.json().then ((collected) => {
        setdata(collected);
    })
    ); 
    }, []);*/
 
  return (
   activeTab === id ? <div className="TabContent">
     { children }
   </div>
   : null
 );
};
 
export default TabContent;