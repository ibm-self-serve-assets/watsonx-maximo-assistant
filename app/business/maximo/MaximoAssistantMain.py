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

                ### Create Chart if required
                waChart = WaChart()
                imageTagText = waChart.generate_chart1()
                result["graph"] = imageTagText

                ### Create html table if required
                tableText = waChart.generate_table1()
                result["table"] = tableText

        end_time = time.time()
        execution_time = end_time - start_time

        self.logger.debug("------------------------------------------------ Final Response ------------------------------------------------")
        self.logger.debug(result)
        self.logger.debug("---------------------------------------------------------------------------------------------------------------")

        self.logger.info(f"Execution time: executeUserQuery : {execution_time} seconds ")
        self.logger.info("=============================================== executeUserQuery Completed ===============================================\n\n\n")
        return result