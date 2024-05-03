import requests
import json
import os
from dotenv import load_dotenv
from ibm_cloud_sdk_core import IAMTokenManager
import time
load_dotenv()

import logging

class LlmHandler:
    
    def __init__(self):
        self.IBMC_AUTH_URL = os.getenv("IBMC_AUTH_URL", None)
        self.WX_APIKEY = os.getenv("WX_APIKEY", None)
        self.WX_ENDPOINT_URL = os.getenv("WX_ENDPOINT_URL", None)
        self.WX_PROJECT_ID = os.getenv("WX_PROJECT_ID", None)
        self.WX_MODEL_ID_NLP = os.getenv("WX_MODEL_ID_NLP", None)
        self.WX_MODEL_ID_SQL = os.getenv("WX_MODEL_ID_SQL", None)
        self.WX_INSTRUCTION1 = os.getenv("WX_INSTRUCTION1", "")
        self.WX_INSTRUCTION2 = os.getenv("WX_INSTRUCTION2", "")
        self.GITHUB_PATH_EXAMPLE_FILE = os.getenv("GITHUB_PATH_EXAMPLE_FILE", "")

        self.EXAMPLES_FILE = "woExamples.txt"
        self.CHART_FILE = "chart.txt"

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())
        
    def callWatsonx(self, project_id, model_id, prompt_input, max_new_tokens):
        self.logger.info("------------------------------------------------ callWatsonx Started ------------------------------------------------")
        start_time = time.time()
        self.logger.info(f"Prompt : {prompt_input} ")

        self.WX_ACCESS_TOKEN = IAMTokenManager(apikey = self.WX_APIKEY, url = self.IBMC_AUTH_URL).get_token()
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer '+ self.WX_ACCESS_TOKEN
            }
        
        parameters = {
            "decoding_method": "greedy",
            "max_new_tokens": max_new_tokens,
            "min_new_tokens": 1,
            "repetition_penalty": 1
            }
        
        llmPayload = {
            "project_id": project_id,
            "model_id": model_id, 
            "parameters": parameters,
            "input": prompt_input
            }
        
        llmResponse = requests.post(self.WX_ENDPOINT_URL, json=llmPayload, headers=headers)
        if llmResponse.status_code == 200:
            output = llmResponse.json()["results"][0]["generated_text"]
        else:
            output = llmResponse.text

        result = {}
        result["status_code"] = llmResponse.status_code
        result["output"] = output
        
        end_time = time.time()
        execution_time = end_time - start_time
        self.logger.info(f"\n\n\nresult : {result} ")
        self.logger.info(f"\nExecution time: callWatsonx : {execution_time} seconds")
        self.logger.debug("------------------------------------------------ callWatsonx Completed ------------------------------------------------\n\n\n")

        return result


    def loadExampleFileData(self):
        self.logger.info("------------------------------------------------ loadExampleFileData Started ------------------------------------------------")
        # woExample = open(self.EXAMPLES_FILE, "r")
        # exampleData = woExample.read() + "\n\n"
        # woExample.close()
        exampleData = self.get_file_from_github()
        self.logger.info(f"Example file content : {exampleData}")                
        self.logger.debug("------------------------------------------------ loadExampleFileData Completed ------------------------------------------------")
        return exampleData
    

    def generateSql(self, query, table, columns):
        self.logger.info("------------------------------------------------ generateSql Started ------------------------------------------------")

        ### Load Examples from file
        exampleData = self.loadExampleFileData()

        ### Context
        columns = columns.replace("}, {", "},\n{")
        context = "\nCONTEXT:\n#####\n\nTABLE: MAXIMO." + table + "\n\nCOLUMNS:\n\n" + columns + "\n\n#####\n"

        ### Prompt
        prompt_input = self.WX_INSTRUCTION1 + context + exampleData + query + "\n"

        ### Call LLM
        llmResponse = self.callWatsonx(self.WX_PROJECT_ID, self.WX_MODEL_ID_SQL, prompt_input, 50)

        self.logger.debug(f"generateSql : result {llmResponse} ")                
        self.logger.debug("------------------------------------------------ generateSql Completed ------------------------------------------------")
        return llmResponse 


    def generateSummary(self, query, sql_output):
        self.logger.info("------------------------------------------------ generateSummary Started ------------------------------------------------")

        prompt_input = self.WX_INSTRUCTION2 + "\n" + query + "\n" + sql_output + "\n\n"

        llmResponse = self.callWatsonx(self.WX_PROJECT_ID, self.WX_MODEL_ID_NLP, prompt_input, 200)

        self.logger.debug(f"generateSummary : result : {llmResponse}")  
        self.logger.debug("------------------------------------------------ generateSummary Completed ------------------------------------------------")
        return llmResponse 


    def get_file_from_github(self):
        self.logger.info("------------------------------------------------ get_file_from_github Started ------------------------------------------------")
        result = None
        try:
            response = requests.get(self.GITHUB_PATH_EXAMPLE_FILE)
            if response.status_code == 200:
                result = response.text
        except requests.RequestException as e:
            self.logger.debug(f"Error fetching file: {e}")
            result = None

        self.logger.debug("------------------------------------------------ get_file_from_github completed ------------------------------------------------")
        return result

