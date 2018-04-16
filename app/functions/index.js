const functions = require('firebase-functions');
const admin = require('firebase-admin');

const express = require("express");
const querystring = require('querystring');

const app = express();

// credentials init
// if we're in our local env, then use credentials.json.
// if this is production, us the firebase config variables
let creds;
if(Object.keys(functions.config()).length == 0){
    const serviceAccount = require("./credentials.json")
    creds = admin.credential.cert(serviceAccount)
} else{
    creds = functions.config().db.creds
    creds = JSON.parse(
        Buffer.from(creds, 'base64').toString('ascii')
    )
}

// init the app with our credentials
admin.initializeApp({
    credentials:creds
});

var db = admin.firestore();

// endpoint to query the jobs by company, stack, location
app.get("/jobs",(request, response) => {
    // get the parameters given by the query string so we can cater to its needs
    let query = querystring.parse(request.url.split("?")[1])
    
    // ask firebase to get all jobs
    db.collection('jobs').get()
    .then((snapshot) => {
        // generate a list of jobs asynchronously
        let jobs = [];
        let i = 0
        snapshot.forEach(job=>{
            jobs.push(job.data());
            // if this is our last item, send the list to the client
            if (i == snapshot._size-1){
                response.json(jobs)
            }
            i++;
        })
    })
    .catch((err) => {
        // in the event of an error, log it to the console and don't tell the client
        // TODO: send error to the client
        console.log(err)
    });
})

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions

exports.app = functions.https.onRequest(app);
