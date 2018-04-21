import React from "react";
import ReactDOM from "react-dom";

import Bootstrap from 'bootstrap/dist/css/bootstrap.css';
import "./index.sass"


const $ = require("jquery");

class Skill extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      companies: props.companies,
      text: props.name
    }
  }
  render() {
    return (
      <div className="card skill">
        <div className="row">
          <h1>{this.state.text}</h1>
        </div>
        <div className="row spacer">
          Lorem ipsum dolor sit amet, etiam voluptua ocurreret nec ut, his dicant expetenda cu. Sea no meis consul. Has atqui laoreet ocurreret in, eu eos unum delectus antiopam.
        </div>
        <div className="row companies">
          <div>
            <ul>
            {
              this
                .state
                .companies
                .map((name,i)=>{
                  return (
                    <li key={i}>
                      <span className={"company-rank" + (i < 3 ? " company-rank-" + (i+1).toString() : "d-none") }>
                      </span>
                      <span style={{margin:4}}>{name}</span>
                    </li>
                  );
                })
            }
            </ul>
          </div>
        </div>
      </div>
    );
  }
}

class QueryResults extends React.Component {
  constructor() {
    super();
    this.state = {
      items: [
        {
          name: "Node.js",
          companies: [
              "Facebook",
              "Google",
              "Amazon",
              "Microsoft"
          ]
        },
        {
          name: "Python",
          companies: [
            "Youtube",
            "SendGrid",
            "Amazon",
            "Netflix"
          ]
        },
        {
          name: "Javascript",
          companies: [
            "Asana",
            "LeetCode",
            "SSIMWAVE",
            "Trello"
          ]
        },
        {
          name: "React",
          companies: [
            "Youtube",
            "SendGrid",
            "Apple",
            "Netflix"
          ]
        },
        {
          name: "C++",
          companies: [
            "Facebook",
            "SendGrid",
            "HackerRank",
            "Netflix"
          ]
        }
      ]
    };
  }

  changeTitle(title) {
    this.setState({title});
  }

  render() {
    return (
      <ul className="results">
        {
          this.state.items.map((item,i)=>
            <li key={i} className="result">
              <Skill 
                name={item.name}
                companies={item.companies}
              />
            </li>
          )
        }
      </ul>
    );
  }
}

class App extends React.Component {
  constructor(props){
    super(props);
  }
  
  render() {
    return (
      <center className="main">
        <QueryResults />
      </center>
    )
  }
}

$(document).ready(()=>{
  const app = $("#app")[0];
  ReactDOM.render(<App/>, app);
})