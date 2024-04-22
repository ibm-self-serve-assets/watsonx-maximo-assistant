from flask import Flask, jsonify, request
from flask_cors import CORS

import os
import argparse
import logging 
import socket
import sys
import json
import os, pandas as pd
# import ibm_db
import requests
from dotenv import load_dotenv
import os, json

from maximo import MaximoHandler
from maximoapp import wxmas

from flask_restx import Api, Resource, fields

app = Flask(__name__, static_folder='./static', static_url_path='/')
CORS(app)

# Initialize Flask-RestX API with OpenAPI version
api = Api(app, version='1.0', title='Watsonx Maximo Assistant API', description='Watsonx Maximo Assistant API', 
          doc='/swagger',  # Route for accessing the Swagger UI
          openapi_version='3.0.2'  # Specify the OpenAPI version here
)

# Define a simple homepage route
@app.route('/')
def home():
    return app.send_static_file('index.html')

ns = api.namespace('maximo', description='Maximo API')

# Define the model for the request payload
input_data_model = api.model('InputData', {
    'query': fields.String(required=True, description='The query to be asked with Maximo')
})
# Define the model for the response payload
output_data_model = api.model('OutputData', {
    'query': fields.String(description='The Given Query'),
    'sql': fields.String(description='The Generated SQL'),
    'json': fields.String(description='The Generate JSON'),
    'response': fields.String(description='The final response for the query'),
})
@ns.route('/')
class MaximoWorld(Resource):
    def get(self):
        maximoHandler = MaximoHandler()
        return maximoHandler.executeGetMain()

    @ns.doc(description='Maximo', responses={200: 'Successful operation', 400: 'Invalid input'})
    @ns.expect(input_data_model)
    @ns.marshal_with(output_data_model)
    def post(self):
        # maximoHandler = MaximoHandler()
        # response = maximoHandler.executePostMain(api.payload)

        wxobj = wxmas()
        response = wxobj.executePostMain(api.payload)

        print("------------------------------------------------ Final Response ------------------------------------------------")
        print(response)
        print("---------------------------------------------------------------------------------------------------------------")
        return response


ns = api.namespace('hello', description='Hello API')
@ns.route('/')
class HelloWorld(Resource):
    def get(self):
        return {'hello': 'world'}

# Sample data
books = [
    {"id": 1, "title": "Book 1", "author": "Author 1"},
    {"id": 2, "title": "Book 2", "author": "Author 2"}
]

ns = api.namespace('books', description='Books operations')
@ns.route('/')
class Books(Resource):
    # API endpoint to get all books
    def get(self):
        return jsonify(books)


def main():
  logging.info("main started .....")


if __name__ == '__main__':
  main()
  app.run(host ='0.0.0.0', port = 8080, debug = True)