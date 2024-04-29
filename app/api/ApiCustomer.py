from flask import Blueprint
from flask_restx import Api, Resource, Namespace, fields

from business.customer.CustomerMain import CustomerMain

customer_ns = Namespace('api/customer', description='Customer operations')

customer_model = customer_ns.model('Customer', {
    'id': fields.Integer(required=True, description='Customer ID'),
    'name': fields.String(required=True, description='Customer name'),
    'email': fields.String(required=True, description='Customer email'),
})

customerMain = CustomerMain()


@customer_ns.route('/')
class CustomerOperations(Resource):
    @customer_ns.doc('list_customers')
    @customer_ns.marshal_list_with(customer_model)
    def get(self):
        return customerMain.getAll()

    @customer_ns.doc('create_customer')
    @customer_ns.expect(customer_model)
    @customer_ns.marshal_with(customer_model, code=201)
    def post(self):
        payload = customer_ns.payload
        return customerMain.create(payload)
