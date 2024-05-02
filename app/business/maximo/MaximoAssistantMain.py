import requests
import json
import os
from dotenv import load_dotenv
import time
import logging
from business.maximo.LlmHandler import LlmHandler
from business.maximo.MaximoHandler import MaximoHandler
from business.maximo.WaChart import WaChart

load_dotenv()

class MaximoAssistantMain:
    
    def __init__(self):
        self.MAS_URL = os.getenv("MAS_URL", None)
        self.MAS_TABLE = os.getenv("MAS_TABLE", None)
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())

    def executeUserQuery(self, payload):
        self.logger.info("=============================================== executeUserQuery Started ===============================================")
        start_time = time.time()

        query = payload['query']
        self.logger.info(f"Query : {query} ")

        result = {}
        result["query"] = query
        result["sql"] = "NA"
        result["json"] = "NA"
        result["response"] = "NA"

        llmHandler = LlmHandler()
        maximoHandler = MaximoHandler()

        ### Get Columns from Maximo
        columns = maximoHandler.getColumns(self.MAS_TABLE)

        ### Generate SQL via LLM
        llmResponse = llmHandler.generateSql(query, self.MAS_TABLE, columns)
        sql = llmResponse["output"]
        result["sql"] = sql

        if llmResponse["status_code"] == 200:
            ### Run SQL in Maximo
            sqlResponse = maximoHandler.runSQL(sql)
            sql_output = json.dumps(sqlResponse["sql_output"])


            result["sql_output_json"] = sql_output

            if sqlResponse["status_code"] == 200:
                ### Generate Summary of Sql Output via LLM
                llmResponse = llmHandler.generateSummary(query, sql_output)
                result["response"] = llmResponse["output"]


                waChart = WaChart()

                ### Create html table if required ----
                json_data = json.loads(sql_output)
                chart_dict = json_data[0]
                keys = list(chart_dict.keys())
                print("keys in response = ",keys)
            
                # Creating the desired format for fields
                fields = [{"name": key} for key in keys]
                table_tag = waChart.generate_table(rows = json_data, fields=fields)
                result["table"] = table_tag

                ### Create Chart if required
                image_tag = None
                #Creating Chart based on sql function and number of json attributes 
                aggregation_functions = ['COUNT', 'SUM', 'AVG', 'MIN', 'MAX', 'GROUP_CONCAT', 'STRING_AGG', 'ARRAY_AGG', 'JSON_ARRAYAGG', 'JSON_OBJECTAGG']
                for func in aggregation_functions:
                    if func in sql and len(keys)<=3:
                        print("chart will be created...") 
                        if "bar" in result['query']:
                            image_tag = waChart.generate_chart(data = json_data,x_field=keys[0] , y_field=keys[1] ,chart_type='bar')
                        elif "pie" in result['query']:
                            image_tag = waChart.generate_chart(data = json_data,x_field=keys[0], y_field=keys[1] ,chart_type='pie')
                        else :
                            image_tag = waChart.generate_chart(data = json_data,x_field=keys[0] , y_field=keys[1] )
                        print(image_tag)
                result["graph"] = image_tag

        end_time = time.time()
        execution_time = end_time - start_time

        self.logger.debug("------------------------------------------------ Final Response ------------------------------------------------")
        self.logger.debug(result)
        self.logger.debug("---------------------------------------------------------------------------------------------------------------")

        self.logger.info(f"Execution time: executeUserQuery : {execution_time} seconds ")
        self.logger.info("=============================================== executeUserQuery Completed ===============================================\n\n\n")
        return result