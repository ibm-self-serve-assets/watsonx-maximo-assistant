import base64
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt

from io import BytesIO
import datetime

import logging
import os

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

    def generate_chart(self, data):
        self.logger.info("------------------------------------------------ generate_chart started -------------------------------------------------\n\n\n")

        # Convert date strings to datetime objects
        dates = [datetime.datetime.fromisoformat(row[0].replace('Z', '')) for row in data]
        values = [row[1] for row in data]

        ### Plot the data
        plt.plot(dates, values)
        plt.xlabel('Date')
        plt.ylabel('Value')
        plt.title('Sample Chart')
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

        self.logger.debug(f"result : {image_tag}")
        self.logger.debug("------------------------------------------------ generate_chart completed -------------------------------------------------\n\n\n")
        return image_tag

    def generate_table(self, rows, fields):
        self.logger.info("------------------------------------------------ generate_table started -------------------------------------------------\n\n\n")

        table = "<table><tr>"
        for field in fields:
            table = table + "<td style='border: 1px solid black; padding: 5px'><strong>" + field["name"] + "</strong></td>"
        table = table + "</tr>"
        for row in rows:
            table = table + "<tr>"
            for item in row:
                if isinstance(item, datetime.datetime):
                    table = table + f"<td style='border: 1px solid black; padding: 5px'>{self.format_date(item)}</td>"
                else:
                    table = table + f"<td style='border: 1px solid black; padding: 5px'>{item}</td>"
            table = table +"</tr>"
        table = table + "</table>"

        self.logger.debug(f"result {table}")
        self.logger.debug("------------------------------------------------ generate_table completed -------------------------------------------------\n\n\n")
        return table
    
    def generate_chart1(self):
        return self.generate_chart(self.data)
    
    def generate_table1(self):
        return self.generate_table(self.data, self.fields)

    def format_date(date):
        # Convert datetime object to a formatted string
        return date.strftime("%Y-%m-%d %H:%M:%S")
