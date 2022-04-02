import React, { useState, useEffect, useRef } from "react";
import { fetchDataAtFixedInterval, resizeViz } from "../helpers/helpers";

const { tableau } = window;

function Dashboard() {
  const [url] = useState(
    "https://clientreporting.theinformationlab.co.uk/t/PublicDemo/views/PabloTest-Donotdelete/Dashboard1"
  );
  const ref = useRef(null);

  let viz;

  const initViz = () => {
    viz = new tableau.Viz(ref.current, url);
    fetchDataAtFixedInterval(viz);
  };

  useEffect(initViz, []);

  useEffect(() => {
    const handleResize = () => {
      resizeViz(viz, window.innerWidth, window.innerHeight);
    };
    window.addEventListener("resize", handleResize);
  });

  return (
    <div ref={ref}></div>
  );
}

export default Dashboard;
