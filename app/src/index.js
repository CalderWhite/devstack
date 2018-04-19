import React from "react";
import ReactDOM from "react-dom";

const $ = require("jquery");

class Layout extends React.Component {
  constructor() {
    super();
    this.state = {
      title: "Welcome",
    };
  }

  changeTitle(title) {
    this.setState({title});
  }

  render() {
    return (
        <p>{this.state.title}</p>
    );
  }
}

$(document).ready(()=>{
    const app = $("#app")[0];
    ReactDOM.render(<Layout/>, app);
})