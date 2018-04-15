const admin = require('firebase-admin');

var serviceAccount = require('./credentials.json');

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount)
});

var db = admin.firestore();


db.collection('jobs').get()
.then((snapshot) => {
    let jobs = [];
    let i = 0
    snapshot.forEach(job=>{
        jobs.push(job.data());
        if (i == snapshot._size-1){
            console.log(jobs)
        }
        i++;
    })
    console.log(snapshot._size)
})
.catch((err) => {
    console.log(err)
});