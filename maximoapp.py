import requests
import json
import os
from dotenv import load_dotenv
from ibm_cloud_sdk_core import IAMTokenManager

load_dotenv()

class wxmas:
    
    def __init__(self):
        self.MAS_URL = os.getenv("MAS_URL", None)
        self.MAS_APIKEY = os.getenv("MAS_APIKEY", None)
        self.IBMC_AUTH_URL = os.getenv("IBMC_AUTH_URL", None)
        self.WX_APIKEY = os.getenv("WX_APIKEY", None)
        self.WX_ENDPOINT_URL = os.getenv("WX_ENDPOINT_URL", None)
        self.WX_PROJECT_ID = os.getenv("WX_PROJECT_ID", None)
        self.WX_MODEL_ID = os.getenv("WX_MODEL_ID", None)
        self.WX_ACCESS_TOKEN = IAMTokenManager(apikey = self.WX_APIKEY, url = self.IBMC_AUTH_URL).get_token()
        self.WO_EXAMPLE_FILE = os.getenv("WO_EXAMPLE_FILE", "woExample.txt")

    def getObjectList(self):
        context = []
        
        url = self.MAS_URL + "/api/os/MXAPIMAXOBJECT"
        params = {
            "lean": "1",
            "ignorecollectionref": "1",
            "oslc.select": "objectname,description",
            "savedQuery": "oobpersistentobj"
        }
        headers = {
            "Content-Type": "application/json",
            "apikey": self.MAS_APIKEY
        }
        
        response = requests.get(url = url, params = params, headers = headers)
        maxobj = response.json()["member"]
        
        for obj in maxobj:
            temp={}
            temp["tablename"] = obj["objectname"]
            temp["description"] = obj["description"]
            
            context.append(temp)
        
        return json.dumps(context)
    
    def getAttributeList(self, tablename):
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
    
        return json.dumps(context)
    
    def runSQL(self, sql):
        url = self.MAS_URL + "/api/script/RUNSQL?lean=1&ignorecollectionref=1"
        
        headers = {
            "Content-Type": "application/json",
            "apikey": self.MAS_APIKEY
        }

        body = {
            "sql": sql
        }

        response = requests.post(url = url, json = body, headers = headers)
        return response
        
    def getWXres(self, project_id, model_id, prompt_input, max_new_tokens):
        #self.WX_ACCESS_TOKEN = IAMTokenManager(apikey = self.WX_APIKEY, url = self.IBMC_AUTH_URL).get_token()
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
        
        response = requests.post(self.WX_ENDPOINT_URL, json=llmPayload, headers=headers)
        return response
        
    def main(self, query):
        result = {}
        result["query"] = query
        result["sql"] = "NA"
        result["json"] = "NA"
        result["response"] = "NA"

        # Generating SQL query using LLM
        instruction = "\nAct as an expert in generating SQL statements for DB2. Understand the table context given below, and find the relevant columns for the given input based on the labels provided. Then generate a SQL query by using only these columns that are provided in the context below. Do NOT create column names by yourself, only use names from the context provided below.\n"
        
        woExample = open(self.WO_EXAMPLE_FILE, "r")
        example = woExample.read() + "\n\n"
        woExample.close()

        objectname = "WORKORDER"
        context = self.getAttributeList(objectname)
        context = context.replace("}, {", "},\n{")
        context = "\nCONTEXT:\n#####\n\nTABLE: MAXIMO." + objectname + "\n\nCOLUMNS:\n\n" + context + "\n\n#####\n"

        prompt_input = instruction + context + example + query + "\n"
        #print(prompt_input)

        sqlGenllmResponse = self.getWXres(self.WX_PROJECT_ID, self.WX_MODEL_ID, prompt_input, 50)

        if sqlGenllmResponse.status_code == 200:
            genSQL_output = sqlGenllmResponse.json()["results"][0]["generated_text"]
        else:
            genSQL_output = sqlGenllmResponse.text
        
        #print(genSQL_output)
        result["sql"] = genSQL_output

        if sqlGenllmResponse.status_code == 200:
            sqlExecResponse = self.runSQL(genSQL_output)
            if sqlExecResponse.status_code == 200:
                sql_output = sqlExecResponse.json()
            else:
                sql_output = sqlExecResponse.text
            
            #print(sql_output)
            result["json"] = json.dumps(sql_output)

            if sqlExecResponse.status_code == 200:
                instruction = "\nThe question below has an answer in JSON format. Convert the JSON response to a natural language response.\n"
                prompt_input = instruction + "\n" + query + "\n" + json.dumps(sql_output) + "\n\n"
                #print(prompt_input)

                json2NLPResponse = self.getWXres(self.WX_PROJECT_ID, self.WX_MODEL_ID, prompt_input, 200)
                #print(json2NLPResponse.json())

                if json2NLPResponse.status_code == 200:
                    nlp_output = json2NLPResponse.json()["results"][0]["generated_text"]
                else:
                    nlp_output = json2NLPResponse.text
        
                #print("Response:")
                #print(nlp_output)
                result["response"] = nlp_output.strip()
        
        return result

    def executePostMain(self, payload):
        query = payload['query']
        result = self.main(query)
        return result

# if __name__ == '__main__':
#     # User input query
#     query = "Get the details for work order 1309"
#     #query = input("Enter the question:\n")
#     wxobj = wxmas()
#     result = wxobj.main(query)
    
#     print("Response:")
#     #print((result["response"]).strip())
#     print(result)