const functions = require('firebase-functions');
const admin = require('firebase-admin');

const express = require('express');
const querystring = require('querystring');

const app = express();

const MAX_RESULTS = 50;
const CACHE_TIME = 60*10;
// this is relative to the MAX_RESULTS. this limit will be adjusted if the user
// voluntarily sets their limit to a lower number. 
// For example. limit=25, therefore the highest page will actually be 4
const MAX_PAGE = 2;

// credentials init
// if we're in our local env, then use credentials.json.
// if this is production, us the firebase config variables
let creds;
if(Object.keys(functions.config()).length == 0){
    // load in the credentials file
    const serviceAccount = require('./credentials.json')
    creds = admin.credential.cert(serviceAccount)
} else{
    // aquire the credentials from firebase config
    creds = functions.config().db.creds
    creds = JSON.parse(
        Buffer.from(creds, 'base64').toString('ascii')
    )
}
/*
let creds = admin.credential.cert(require("./credentials.json"));
*/
// init the app with our credentials
admin.initializeApp({
    credentials:creds
});

var db = admin.firestore();


function firebaseSafeEncode(s){
    s = Buffer.from(s).toString('base64');
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
    return Buffer(
        s.substring(1,s.length) + '='.repeat(pad),
        'base64'
    ).toString('ascii');
}
function returnQuery(request, response, query, ref) {
    // get limit
    let limit = MAX_RESULTS
    if (Object.keys(query).includes('limit')) {
        limit = Math.min(Number(query.limit),MAX_RESULTS);
    }
    let page = 1
    if (Object.keys(query).includes('page')) {
        page = Math.min(
            Number(query.page),
            MAX_PAGE*(MAX_RESULTS/limit) - 1
        )
    }
    
    // apply query limits
    if (page != 1){
        ref = ref
            .startAt((page-1)*limit)
    }
    ref = ref.limit(limit)
   
    console.log("Getting...")
    // ask firebase to get all jobs
    ref.get()
    .then((snapshot) => {
        // check if there are no results, so we don't leave the user hanging
        if (snapshot.size == 0){
            response.json([])
        }
        
        // generate a list of jobs asynchronously
        let jobs = [];
        let i = 0
        snapshot.forEach(job=>{
            jobs.push(job.data());
            // if this is our last item, send the list to the client
            if (i == snapshot._size-1){
                // cachings
                //response.set('Cache-Control', 'public, max-age=' + CACHE_TIME.toString() + ', s-maxage' + CACHE_TIME.toString());
                response.json(jobs)
            }
            i++;
        })
    })
    .catch((err) => {
        // in the event of an error, log it to the console and don't tell the client
        // TODO: send error to the client
        console.log(err)
        response
            .status(500)
            .send("Error occurred retrieving positions.")
    });
}

// endpoint for skills sorted by amount of companies using it
app.get('/skills',(request,response) => {
    let query = querystring.parse(request.url.split('?')[1])
    let ref = db.collection('skills');
    
    ref = ref.orderBy('totalCompanies','desc');
    
    returnQuery(request, response, query, ref);
})

// endpoint to query the jobs by company, stack, location
app.get('/jobs',(request, response) => {
    // get the parameters given by the query string so we can cater to its needs
    let query = querystring.parse(request.url.split('?')[1])
    let ref = db.collection('jobs');
    
    // filtering by skills
    if (Object.keys(query).includes('skills')) {
        let skills = query.skills.split(',');;
        for (let i = skills.length; i--; ) {
            console.log(firebaseSafeEncode(skills[i]))
            ref = ref.where(
                'stack.' + firebaseSafeEncode(skills[i]),
                '==',
                true
            );
        }
        
    }
    
    // filtering by location
    if (Object.keys(query).includes('location')) {
        ref = ref.where(
            "location",
            "==",
            query.location
        );
    }
    
    returnQuery(request, response, query, ref);
})

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions

exports.app = functions.https.onRequest(app);
//app.listen(8080)