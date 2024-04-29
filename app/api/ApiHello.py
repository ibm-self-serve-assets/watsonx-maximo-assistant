from flask_restx import Namespace, Resource

hello_ns = Namespace('hello', description='Hello operations')
@hello_ns.route('/')
class HelloWorld(Resource):
    def get(self):
        result = {'hello': 'world'}
        return result, 200