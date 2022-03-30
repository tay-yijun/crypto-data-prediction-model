import React from "react";
import { BrowserRouter as Router, Link } from "react-router-dom";

import Main from "./Main";

function Header() {
  return (
    <Router>
      <div className="App">
        <nav className="navBar">
          <ul>
            <li>
              <Link to="/">Home</Link>
            </li>
            <li>
              <Link
                to={{
                  pathname: "/embed/",
                  state: {
                    title: "Basic Embed"
                  }
                }}
              >
                Basic Embed
              </Link>
            </li>
            <li>
              <Link to="/animation">Animation</Link>
            </li>
          </ul>
        </nav>

        <Main />
      </div>
    </Router>
  );
}

export default Header;
