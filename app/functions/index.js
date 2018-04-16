const functions = require('firebase-functions');
const admin = require('firebase-admin');

const express = require('express');
const querystring = require('querystring');

const app = express();

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

// endpoint to query the jobs by company, stack, location
app.get('/jobs',(request, response) => {
    // get the parameters given by the query string so we can cater to its needs
    let query = querystring.parse(request.url.split('?')[1])
    let ref = db.collection('jobs');
    console.log(query)
    
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
    
    // for now, limit queries to 100 results
    ref = ref.limit(100)
    console.log("Getting...")
    // ask firebase to get all jobs
    ref.get()
    .then((snapshot) => {
        // generate a list of jobs asynchronously
        let jobs = [];
        let i = 0
        snapshot.forEach(job=>{
            jobs.push(job.data());
            // if this is our last item, send the list to the client
            if (i == snapshot._size-1){
                // cachings
                let cacheTime = (60*10).toString();
                response.set('Cache-Control', 'public, max-age=' + cacheTime + ', s-maxage' + cacheTime);
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
})

// // Create and Deploy Your First Cloud Functions
// // https://firebase.google.com/docs/functions/write-firebase-functions

exports.app = functions.https.onRequest(app);
//app.listen(8080)