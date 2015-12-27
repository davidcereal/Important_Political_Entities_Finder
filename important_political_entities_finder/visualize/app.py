import flask
import requests
from flask import request

import whoosh.index as index
from whoosh.index import open_dir

import search_index as si

## Load index for searching
index= index.open_dir("important_political_entities_finder/wrangle/index")
print 'index loaded'





#---------- URLS AND WEB PAGES -------------#

# Initialize the app
app = flask.Flask(__name__, template_folder='templates', static_folder='static')

## Homepage
@app.route("/")
def viz_page():
    """
    Homepage: serve our visualization page, index.html
    """
    return flask.render_template('index.html')

## Get an example and return it's score from the predictor model
@app.route("/results", methods=["POST"])
def score():
    """
    When A POST request with json data is made to this uri,
    Read the example from the json, search for topic and
    send results as a response
    """
## Get results from search topic that came with request
    data = flask.request.json
    search_term = data["example"][0]
    start_date =  data["example"][1]
    stop_date =  data["example"][2]
    parsed_results = si.search_topic(index, search_term, start_date, stop_date)

## Put the result in a nice dict so we can send it as json
    return_data = {'name': 'flare', "children": [{'name': 'cluster', 'children': parsed_results}]}
    return flask.jsonify(return_data)

#--------- RUN WEB APP SERVER ------------#

# Start the app server on port 80
# (The default website port)
app.run(host= '0.0.0.0', port=5000, debug=True)



