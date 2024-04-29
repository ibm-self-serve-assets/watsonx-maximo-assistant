from flask_restx import Namespace, Resource, fields

from business.maximo.MaximoAssistantMain import MaximoAssistantMain

maximo_ns = Namespace('maximo', description='Maximo Operations')

# Define the model for the request payload
input_data_model = maximo_ns.model('InputData', {
    'query': fields.String(required=True, description='The query to be asked with Maximo')
})
# Define the model for the response payload
output_data_model = maximo_ns.model('OutputData', {
    'query': fields.String(description='The Given Query'),
    'sql': fields.String(description='The Generated SQL'),
    'json': fields.String(description='The Generate JSON'),
    'response': fields.String(description='The final response for the query'),
    'graph': fields.String(description='The graph response for the query'),
    'table': fields.String(description='The table response for the query'),
})

@maximo_ns.route('/')
class MaximoWorld(Resource):
    @maximo_ns.doc(description='Maximo', responses={200: 'Successful operation', 400: 'Invalid input'})
    @maximo_ns.expect(input_data_model)
    @maximo_ns.marshal_with(output_data_model)
    def post(self):
        print(" Maximo ....")
        maximoAssistantMain = MaximoAssistantMain()
        response = maximoAssistantMain.executeUserQuery(maximo_ns.payload)
        return response
