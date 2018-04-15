const functions = require('firebase-functions');
const admin = require('firebase-admin');

const express = require("express");
const querystring = require('querystring');

const app = express();

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

admin.initializeApp({
    credentials:creds
});

var db = admin.firestore();

app.get("/companies",(request, response) => {
    let query = querystring.parse(request.url.split("?")[1])
    
    db.collection('jobs').get()
    .then((snapshot) => {
        let jobs = [];
        let i = 0
        snapshot.forEach(job=>{
            jobs.push(job.data());
            if (i == snapshot._size-1){
                response.json(jobs)
            }
            i++;
        })
    })
    .catch((err) => {
        console.log(err)
    });
})

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions

exports.app = functions.https.onRequest(app);
