import React from "react";
import { Route } from "react-router-dom";

import BasicEmbed from "../components/BasicEmbed";
import Home from "../components/Home";
import Animation from "../components/Animation";

function Main() {
  return (
    <section>
      <Route path="/" exact component={Home} />
      <Route path="/embed/" component={BasicEmbed} />
      <Route path="/animation/" component={Animation} />
    </section>
  );
}

export default Main;
