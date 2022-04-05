import React, { useState, useEffect, useRef } from "react";
import { fetchDataAtFixedInterval, resizeViz } from "../helpers/helpers";

const { tableau } = window;

function Dashboard() {
  const [url] = useState(
    "https://prod-apnortheast-a.online.tableau.com/t/cryptoviz/views/CryptoDashboard/CryptoDashboard"
  );
  const ref = useRef(null);

  let viz;

  const handleResize = () => {
    resizeViz(viz, window.innerWidth, window.innerHeight);
  };

  const options = {
    hideTabs: true,
    hideToolbar: true,
    onFirstInteractive: () => handleResize(),
  };

  const initViz = () => {
    viz = new tableau.Viz(ref.current, url, options);
    fetchDataAtFixedInterval(viz);
  };

  useEffect(initViz, []);

  useEffect(() => {
    window.addEventListener("resize", handleResize);
  });

  return (
    <div ref={ref}></div>
  );
}

export default Dashboard;
