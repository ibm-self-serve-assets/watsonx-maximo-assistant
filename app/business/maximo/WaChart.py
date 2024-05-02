import base64
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from io import BytesIO
import datetime

import logging
import os
import json

class WaChart:

    def __init__(self):
        self.test = None
        self.data =[
            [ "2022-01-15T18:30:00.000Z", 14.6 ],
            [ "2022-04-19T18:30:00.000Z", 12 ],
            [ "2022-05-31T18:30:00.000Z", 13.3 ],
            [ "2022-07-23T18:30:00.000Z", 13.3 ],
            [ "2022-08-15T18:30:00.000Z", 12 ],
            [ "2022-11-02T18:30:00.000Z", 11.6 ],
            [ "2022-12-21T18:30:00.000Z", 12.5 ],
            [ "2023-02-20T18:30:00.000Z", 13.1 ]
            ]
        # image_tag = generate_chart(data)
        self.fields = [{"name": "Date"}, {"name": "Value"}]

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())
        self.WX_AGGREGATION_FUNCTIONS = os.getenv("WX_AGGREGATION_FUNCTIONS", "")


    ### Creating Chart based on sql function and number of json attributes 
    def generate_chart_and_graph(self, query, sql, sql_output):
        self.logger.info("------------------------------------------------ generate_chart_and_graph started -------------------------------------------------\n\n\n")
        result = {}
        result["table"] = None 
        result["graph"] = None 

        ### Create Table and Chart
        json_data = json.loads(sql_output)
        if json_data and len(json_data) > 0 :

            # Extract fields from the first row
            fields = list(json_data[0].keys())

            ### Create html table
            result["table"] = self._generate_table(json_data, fields)

            if len (fields) == 2 :
                result["graph"] = self._generate_chart_after_validation(query, sql, json_data, fields)
        
        self.logger.debug("------------------------------------------------ generate_chart_and_graph completed -------------------------------------------------\n\n\n")
        return result


    ### Creating Chart based on sql function and number of json attributes 
    def _generate_chart_after_validation(self, query, sql, json_data, fields):
        self.logger.info("------------------------------------------------ generate_chart_after_validation started -------------------------------------------------\n\n\n")

        image_tag = None

        ### Check chart is possible
        chartFlag = False        
        aggregation_functions = self.WX_AGGREGATION_FUNCTIONS.split('###')
        for func in aggregation_functions:
            if func.lower() in sql :
                chartFlag = True
                break
        self.logger.debug(f"generate_chart : chartFlag : {chartFlag}")
 
        if chartFlag : 
            ### Chart Type
            chart_type = "line"
            if " bar " in query:  
                chart_type = "bar"
            elif " pie " in query:
                chart_type = "pie"
            self.logger.debug(f"generate_chart : chart_type : {chart_type}")

            ### Generate Chart
            image_tag = self._generate_chart(json_data, fields, chart_type)
        self.logger.debug("------------------------------------------------ generate_chart_after_validation completed -------------------------------------------------\n\n\n")
        return image_tag

    def _generate_chart(self , data, fields, chart_type):

        self.logger.info("------------------------------------------------ generate_chart started -------------------------------------------------\n\n\n")
 
        x_field = fields[0]
        y_field = fields[1]

        # Extract data for plotting
        x_values = [row[fields[0 ]] for row in data]
        y_values = [row[fields[1]] for row in data]

        # Plot the data based on chart type    
        if chart_type == 'bar':
            plt.bar(x_values, y_values)
        elif chart_type == 'pie':
            plt.pie(y_values, labels=x_values)
        else:
            plt.plot(x_values, y_values)

        # Customize plot
        plt.xlabel(x_field.capitalize())
        plt.ylabel(y_field.upper())
        plt.title('Maximo Assistant Chart')
        plt.xticks(rotation=45)  # Rotate x-axis labels for better readability
        plt.tight_layout()

        # Convert the plot to a bytes object
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)

        # Encode the bytes object as base64
        image_data = base64.b64encode(buffer.getvalue()).decode('utf-8')

        # Construct the image tag
        image_tag = f'<img class="WACImage__Image WACImage__Image--loaded" src="data:image/png;base64,{image_data}" alt="" style="display: block;"/>'
        self.logger.debug("------------------------------------------------ generate_chart completed -------------------------------------------------\n\n\n")

        return image_tag

    def _generate_table(self, json_data, fields):
        self.logger.info("------------------------------------------------ generate_table started -------------------------------------------------\n\n\n")

        table = "<table><tr>"
        # Generate table headers
        for field in fields:
            table += f"<td style='border: 1px solid black; padding: 5px'><strong>{field}</strong></td>"
        table += "</tr>"
        
        # Generate table rows
        for row in json_data:
            table += "<tr>"
            for field in fields:
                item = row[field]
                if isinstance(item, datetime.datetime):
                    table += f"<td style='border: 1px solid black; padding: 5px'>{self._format_date(item)}</td>"
                else:
                    table += f"<td style='border: 1px solid black; padding: 5px'>{item}</td>"
            table += "</tr>"
        table += "</table>"
        
        self.logger.debug(f"result {table}")
        self.logger.info("------------------------------------------------ generate_table completed -------------------------------------------------\n\n\n")

        return table    

    def _format_date(date):
        # Convert datetime object to a formatted string
        return date.strftime("%Y-%m-%d %H:%M:%S")
