import logging 

class CustomerMain(object):

    def __init__(
        self
    ) -> None:
        self.customers = []

    def getAll(self):
        return self.customers

    def create(self, dataIn):
        self.customers.append(dataIn)
        return dataIn, 200