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
import getpass


class MaximoHandler(object):

    model_id = "ibm/granite-13b-instruct-v2"

    parameters = {
        "decoding_method": "greedy",
        "max_new_tokens": 50,
        "repetition_penalty": 1
    }

    instruction = """
        Act as an expert in generating SQL statements. Understand the table context given below, and then generate a SQL query for the given input.
        """

    example = """
        How many work orders are currently in progress?
        select count(1) from maximo.workorder where status='INPRG'; --<end of SQL>

        How many preventive maintainance work orders are stuck due to material unavailablity?
        select count(1) from maximo.workorder where worktype='PM' and status='WMATL'; --<end of SQL>

        Get the details of corrective maintenance work orders waiting for approval?
        select * from maximo.workorder where worktype='CM' and and status='WAPPR'; --<end of SQL>

        Get the details for all work orders reported in the last quarter?
        select * from maximo.workorder where reportdate > (sysdate - 90); --<end of SQL>

        What are the child work order details from the FREO site?
        select * from maximo.workorder where parent is not null and siteid='FREO'; --<end of SQL>

        Calculate the average estimated material cost for preventive maintenance work orders in BEDFORD site.
        SELECT avg(estmatcost) FROM maximo.workorder WHERE siteid = 'BEDFORD' AND worktype = 'PM'; --<end of SQL>

        Fetch work order details of work order 1225.
        select * from maximo.workorder where wonum='1225'; --<end of SQL>

        """

    def getSchema(self, tablename):
        context = []
        ix = 0

        MAXIMO_ATTRRIBUTE_URL = os.getenv("MAXIMO_ATTRRIBUTE_URL", None)
        MAXIMO_API_KEY = os.getenv("MAXIMO_API_KEY", None)

        #objectname = "objectname = '" + tablename + "'"
        url = MAXIMO_ATTRRIBUTE_URL + tablename + "%22"
        params = {
            "lean": "1",
            "ignorecollectionref": "1",
            "oslc.select": "attributename,title,remarks,maxtype"
        }
        headers = {
            "Content-Type": "application/json",
            "apikey": MAXIMO_API_KEY
        }
        
        response = requests.get(url = url, params = params, headers = headers)
        maxattr = response.json()["member"]
        
        for attr in maxattr:
            if not (attr["attributename"].startswith("PLUS")):
                temp={}
                temp["columnname"] = attr["attributename"]
                #temp["label"] = attr["title"]
                temp["description"] = attr["remarks"]
                temp["datatype"] = attr["maxtype"]
            
                #Convert to data type to VARCHAR/DECIMAL/INTEGER/DATETIME
                if temp["datatype"] in ["UPPER","LOWER","ALN"]:
                    temp["datatype"] = "VARCHAR"
                
            context.append(temp)
            ix = ix+1
            if ix == 100:
                break
        
        return json.dumps(context)


    def runSQL(self, sql):

        MAXIMO_RUNSQL_URL = os.getenv("MAXIMO_RUNSQL_URL", None)
        MAXIMO_API_KEY = os.getenv("MAXIMO_API_KEY", None)

        url = MAXIMO_RUNSQL_URL
        headers = {
            "Content-Type": "application/json",
            "apikey": MAXIMO_API_KEY
        }
        body = {
            "sql": sql
        }
        response = requests.post(url = url, json = body, headers = headers)
        if response.status_code == 200:
            return response.json()
        else:
            return response.text


    def call_generative_ai(self, llmPayload):
        GENAI_KEY = os.getenv("GENAI_KEY", None)
        GENAI_API = os.getenv("GENAI_API", None)

        access_token = IAMTokenManager(
            apikey = GENAI_KEY,
            url = "https://iam.cloud.ibm.com/identity/token"
        ).get_token()

        ENDPOINT_URL = GENAI_API
        print("------------------------------------------------ LLM URL ------------------------------------------------")
        print(f'ENDPOINT_URL: {ENDPOINT_URL}')
        print("---------------------------------------------------------------------------------------------------------------")
        headers =  {"Content-Type":"application/json", "Accept": "application/json", "Authorization": "Bearer " +access_token}

        response = requests.post(ENDPOINT_URL, json=llmPayload, headers=headers)
        jsonResp = response.json()
        
        if not 'results' in jsonResp or len(jsonResp['results']) == 0:
            prompt_output = jsonResp
        else:
            prompt_output = jsonResp["results"][0]["generated_text"]

        print("------------------------------------------------ Prompt Output ------------------------------------------------")
        print(prompt_output)
        print("---------------------------------------------------------------------------------------------------------------")

        return prompt_output
    

    def executeGetMain(self):
        query = """
            What is the worktype of workorder 1309?
            """
        return self.executeMain(query)

    def executePostMain(self, payload):
        query = payload['query']
        return self.executeMain(query)

    def executeMain(self, query):

        objectname="WORKORDER"
        context = self.getSchema(objectname)

        context = """
            CONTEXT:
            #####

            TABLE: MAXIMO.""" + objectname + """

            COLUMNS:

            """ + context + """

            #####
            """

        prompt_input = MaximoHandler.instruction + context + MaximoHandler.example + query
        print("------------------------------------------------ Prompt Input ------------------------------------------------")
        print(prompt_input)
        print("---------------------------------------------------------------------------------------------------------------")

        GENAI_PROJECT_ID = os.getenv("GENAI_PROJECT_ID", None)
        llmPayload = {
                    "model_id": MaximoHandler.model_id, 
                    "input": prompt_input, 
                    "parameters": MaximoHandler.parameters,
                    "project_id": GENAI_PROJECT_ID
        }

        ### Call Generative AI
        prompt_output = self.call_generative_ai(llmPayload) 

        ### Run SQL
        response = self.runSQL(prompt_output)
        print("------------------------------------------------ Sql Output ------------------------------------------------")
        print(response)
        print("---------------------------------------------------------------------------------------------------------------")

        result = {
            "result" : response
        }

        print("------------------------------------------------ result ------------------------------------------------")
        print(result)
        print("---------------------------------------------------------------------------------------------------------------")

        return result
