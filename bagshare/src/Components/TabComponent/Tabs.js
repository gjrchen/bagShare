import React from "react";
import { useState } from "react";
import CheckOutTab from "../AllTabs/CheckOutTab";
import ReturnTab from "../AllTabs/ReturnTab";
import StoreadminTab from "../AllTabs/StoreadminTab";
import TabNavItem from "./tabnav";
import TabContent from "./tabcontent";


const Tabs = () => {
    const[activeTab, setactiveTab] = useState("CheckOutTab");

    return (
        <div className="Tabs">
          <ul className="nav">
            <TabNavItem title="Check Out" id="CheckOutTab" activeTab={activeTab} setActiveTab={setactiveTab}/>
            <TabNavItem title="Return" id="ReturnTab" activeTab={activeTab} setActiveTab={setactiveTab}/>
            <TabNavItem title="Store Admin" id="StoreadminTab" activeTab={activeTab} setActiveTab={setactiveTab}/>
          </ul>
     
          <div className="outlet">
            <TabContent id="CheckOutTab" activeTab={activeTab}>
              <CheckOutTab/>
            </TabContent>
            <TabContent id="ReturnTab" activeTab={activeTab}>
              <ReturnTab/>
            </TabContent>
            <TabContent id="StoreadminTab" activeTab={activeTab}>
              <StoreadminTab/>
            </TabContent>
          </div>
        </div>
      );
    };


export default Tabs;
