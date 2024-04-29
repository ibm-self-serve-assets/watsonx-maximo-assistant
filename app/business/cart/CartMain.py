import logging 
import os

class CartMain(object):

    def __init__(
        self
    ) -> None:
        self.cart = []

    def getAll(self):
        return self.cart

    def create(self, dataIn):
        self.cart.append(dataIn)
        return dataIn, 200