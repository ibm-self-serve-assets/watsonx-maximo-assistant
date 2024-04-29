import requests
import json
import os
from dotenv import load_dotenv
from ibm_cloud_sdk_core import IAMTokenManager
import time
import logging

load_dotenv()

class MaximoHandler:
    
    def __init__(self):
        self.MAS_URL = os.getenv("MAS_URL", None)
        self.MAS_APIKEY = os.getenv("MAS_APIKEY", None)

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())


    def getColumns(self, tablename):
        self.logger.info("------------------------------------------------ getColumns Started ------------------------------------------------")
        start_time = time.time()
        self.logger.debug(f"TableName  : {tablename}")

        context = []
        ix = 0
        
        url = self.MAS_URL + "/api/os/MXAPIMAXATTRIBUTE?oslc.where=objectname=%22" + tablename + "%22"
        
        params = {
            "lean": "1",
            "ignorecollectionref": "1",
            "oslc.select": "attributename,title,remarks,maxtype",
            "savedQuery": "oobpersistentattr"
            }

        headers = {
            "Content-Type": "application/json",
            "apikey": self.MAS_APIKEY
            }
        
        response = requests.get(url = url, params = params, headers = headers)
        maxattr = response.json()["member"]

        for attr in maxattr:
            temp = {}
            temp["columnname"] = attr["attributename"]
            temp["datatype"] = attr["maxtype"]
            temp["label"] = attr["title"]
            #temp["description"] = attr["remarks"]

            #Convert to data type to VARCHAR/NUMBER/TIMESTAMP
            if temp["datatype"] in ["ALN","BLOB","CLOB","CRYPTO","CRYPTOX","GL","LONGALN","LOWER","UPPER"]:
                temp["datatype"] = "VARCHAR"
            elif temp["datatype"] in ["AMOUNT","BIGINT","DECIMAL","DURATION","FLOAT","INTEGER","SMALLINT"]:
                temp["datatype"] = "NUMBER"
            elif temp["datatype"] in ["DATE","TIME","DATETIME"]:
                temp["datatype"] = "TIMESTAMP"
            elif temp["datatype"] in ["YORN"]:
                temp["datatype"] = "BOOLEAN"
                
            context.append(temp)
            ix = ix+1
            if ix == 100:
                break

        result = json.dumps(context)    

        end_time = time.time()
        execution_time = end_time - start_time

        self.logger.debug(f"\n\nresult : {result}")
        self.logger.debug(f"\nExecution time: getColumns : {execution_time} seconds")                
        self.logger.debug("------------------------------------------------ getColumns Completed -------------------------------------------------\n\n\n")

        return result


    def runSQL(self, sql):
        self.logger.info("------------------------------------------------ runSQL Started ------------------------------------------------")
        start_time = time.time()
        self.logger.debug(f"Sql : {sql}")                

        url = self.MAS_URL + "/api/script/RUNSQL?lean=1&ignorecollectionref=1"
        headers = {
            "Content-Type": "application/json",
            "apikey": self.MAS_APIKEY
        }
        body = {
            "sql": sql
        }

        response = requests.post(url = url, json = body, headers = headers)
        if response.status_code == 200:
            sql_output = response.json()
        else:
            sql_output = response.text

        result = {}
        result["status_code"] = response.status_code
        result["sql_output"] = sql_output

        end_time = time.time()
        execution_time = end_time - start_time

        self.logger.debug(f"\n\nresult {result}")
        self.logger.debug(f"\nExecution time: runSQL : {execution_time} seconds")                
        self.logger.debug("------------------------------------------------ runSQL Completed -------------------------------------------------\n\n\n")

        return result