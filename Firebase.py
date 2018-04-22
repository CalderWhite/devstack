import os
import base64
import json

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from DevStackBoard.StackParser import PositionSummary

class Firebase(object):
    def __init__(self,env_name):
        
        # decode the ENV variable of our credentials
        
        creds = json.loads(
            base64.b64decode(
                os.environ[env_name]
            ).decode('utf-8')
        )
        
        # load them into firebase
        cred = credentials.Certificate(creds)
        firebase_admin.initialize_app(cred)
        
        self.db = firestore.client()

    def firebase_safe_encode(self,s):
        """
        Since firestore can't handle a key value pairing where the key can't also be a variable name,
        I created an encoding method for the keys. It simply uses base64 encoding but removes the "=" padding from the end and inserts a character before the string
        indicating how much padding is required. This kills 2 birds with one stone since "=" aren't allowed in the names, and numbers can't begin the name.
        """
        s = base64.b64encode(s.encode("utf-8")).decode('utf-8')
        i = len(s) - 1
        while i > 0 and s[i] == "=":
            i -= 1
        c = len(s) - i - 1
        meta = chr(97 + c)
        # could do this better, but this is easier
        return meta + s.replace("=","")

    def firebase_safe_decode(self,s):
        """
        See firebase_safe_encode
        """
        pad = ord(s[0]) - 97
        return base64.b64decode((s[1:] + "="*pad).encode('utf-8')).decode('utf-8')
    
    def add_item(self,j,path):
        # safe encode the item's contents for queries
        if path == "jobs":
            # safe encode the stack so we can query by it later on
            for i in range(len(j.stacks)):
                for k in range(len(j.stacks[i])):
                    j.stacks[i][k] = self.firebase_safe_encode(j.stacks[i][k])
        elif path == "skills":
            new_companies = {}
            for i in j.companies:
                new_companies[
                    self.firebase_safe_encode(i)
                ] = j.companies[i]
            j.companies = new_companies
        else:
            raise Exception("Unknown path.")
        
        data = j.to_dict()
        if self.batch == None:
            self.db.collection(path).add(data)
        else:
            ref = self.db.collection(path).document()
            self.batch.set(ref,data)
    
    def new_batch(self):
        self.batch = self.db.batch()
    
    def commit_batch(self):
        self.batch.commit()
        self.batch = None
        
def main():
    f = Firebase("DEVSTACK_FIREBASE")
    f.new_batch()
    f.add_job(PositionSummary(
        "Senior Software Engineer",
        "Google",
        "Waterloo, Ontario",
        [
            ['Java', 'NoSQL', 'HTML5', 'CSS3', 'Javascript', 'node.js'], 
            ['performance', 'i18n', 'security']
        ]
    ))
    f.add_job(PositionSummary(
        "Senior Software Engineer",
        "Facebook",
        "Toronto, Ontario",
        [
            ['C++', "angular"], 
            ['security']
        ]
    ))
    f.commit_batch()

if __name__ == "__main__":
    main()