import React from "react";
import ReactDOM from "react-dom";

import Bootstrap from 'bootstrap/dist/css/bootstrap.css';
import "./index.sass"


const $ = require("jquery");

function firebaseSafeEncode(s){
    s = btoa(s);
    let i = s.length - 1;
    while(s[i] == '=' && i > 0) {
        i --;
    }
    let c = s.length - i - 1;
    let meta = String.fromCharCode(97 + c);
    
    return meta + s.replace(/\=/g,'');
}
function firebaseSafeDecode(s){
    let pad = s.charCodeAt(0) - 97;
    return atob(
      s.substring(1,s.length) + '='.repeat(pad)
    )
}

class Skill extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      companies: props.companies,
      text: props.name
    }
    //console.log(this.state.companies)
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
                .map((item,i)=>{
                  return (
                    <li key={i} title={item.name} >
                      <span className={"company-rank" + (i < 3 ? " company-rank-" + (i+1).toString() : "d-none") }>
                      </span>
                      <span style={{margin:4}}>{item.name.length > 15 ? item.name.substring(0,16) + "..." : item.name}</span>
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
      page : 1,
      updating : false, 
      items : []
    };
    this.addItems = this.addItems.bind(this);
    this.onScroll = this.onScroll.bind(this);
    
    this.addItems("skills");
  }
  
  addItems(collection) {
    console.log(this.state.page);
    let url = window.location.protocol + "//" + window.location.host + "/" + collection + "?page=" + this.state.page.toString() + "&limit=10";
    console.log(url);
    let comp = this;
    $.getJSON(url, data => {
      let newItems = this.state.items;
      for(let i = 0; i < data.length; i++) {
        let companies = [];
        for (let j in data[i].companies) {
          companies.push({
            name : firebaseSafeDecode(j),
            count : data[i].companies[j]
          });
        }
        // sort in descending order
        companies.sort((a, b) => {
          return a.count - b.count;
        });
        companies.reverse();
        // set the newly reconstructed company list
        data[i].companies = companies;
      }
      console.log(data);
      newItems = newItems.concat(data);

      comp.setState({
        page: this.state.page + 1,
        items : newItems,
        updating : false
      });
    });
  }

  onScroll(event) {
    // check if the scroll is near the bottom
    let scroll = this.refs.results.scrollTop;
    let height = this.refs.results.scrollHeight - this.refs.results.clientHeight;
    // also check that we have not exceed the max pages
    if(height - scroll < 100 && this.state.page < 10 && !this.state.updating) {
      // prevent multiple calls
      this.setState({
        updating: true
      })
      // update
      this.addItems("skills");
    }
  }

  render() {
    return (
      <ul className="results" ref="results" onScroll={this.onScroll}>
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