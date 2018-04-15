import os

from flask import Flask, jsonify, redirect

app = Flask(__name__)

HOST = "0.0.0.0"
PORT = int(os.environ["PORT"])

class Routes:
    class Api:
        @staticmethod
        @app.route('/api')
        def api():
            """Easy way to tell whether or not the server is running."""
            return jsonify({
                "message" : "OK",
                "status_code" : 200
            })
        @staticmethod
        @app.route("/api/")
        def get_companies():
            
    class Pages:
        @staticmethod
        @app.route('/')
        def index():
            """Until the React app is finished, redirect to the github page."""
            return redirect("https://github.com/CalderWhite/dev-stack-board")

app.run(host=HOST,port=PORT )