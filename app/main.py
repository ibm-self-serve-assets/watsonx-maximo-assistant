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

from flask_restx import Api, Resource, fields

app = Flask(__name__, static_folder='./static', static_url_path='/')
CORS(app)

from api.ApiBook import book_ns
from api.ApiCart import cart_ns
from api.ApiCustomer import customer_ns
from api.ApiHello import hello_ns
from api.ApiMaximo import maximo_ns

app = Flask(__name__)
api = Api(app, version='1.0', title='Watsonx Maximo Assistant API Application', 
          description='Watsonx Maximo Assistant API Application', 
          doc='/swagger/',  # Route for accessing the Swagger UI
          openapi_version='3.0.2'  # Specify the OpenAPI version here
)

# Add namespaces (Namespaces)
api.add_namespace(book_ns)
api.add_namespace(cart_ns)
api.add_namespace(customer_ns)
api.add_namespace(hello_ns)
api.add_namespace(maximo_ns)

### Logging Configuration
logging.basicConfig(
    format='%(asctime)s - %(levelname)s:%(message)s',
    handlers=[
        logging.StreamHandler(), #print to console
    ],
    level=logging.INFO
)

### Define a simple homepage route
@app.route('/')
def index():
    return app.send_static_file('index.html')

### Main method
def main():
  logging.info("main started .....")

### Start the Main method
if __name__ == '__main__':
  main()
  app.run(host ='0.0.0.0', port = 8080, debug = True)    