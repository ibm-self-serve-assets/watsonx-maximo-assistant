from flask_restx import Namespace, Resource, fields

from business.cart.CartMain import CartMain

cart_ns = Namespace('api/cart', description='Cart operations')

cart_model = cart_ns.model('Cart', {
    'id': fields.Integer(required=True, description='Cart ID'),
    'product': fields.String(required=True, description='Product name'),
    'quantity': fields.Integer(required=True, description='Quantity'),
})

cartMain = CartMain()

@cart_ns.route('/')
class CartOperations(Resource):
    @cart_ns.doc('list_carts')
    @cart_ns.marshal_list_with(cart_model)
    def get(self):
        return cartMain.getAll()

    @cart_ns.doc('create_cart')
    @cart_ns.expect(cart_model)
    @cart_ns.marshal_with(cart_model, code=201)
    def post(self):
        payload = cart_ns.payload
        return cartMain.create(payload)
