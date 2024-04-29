import logging 
import os

class CartMain(object):

    def __init__(
        self
    ) -> None:
        self.cart = []
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(os.environ.get('LOGLEVEL', 'INFO').upper())

    def getAll(self):
        logging.info("CartMain : getAll : " + str(self.cart))
        logging.info("CartMain : MY_ENV_TEST1 : " + os.environ.get('MY_ENV_TEST1'))
        logging.info("CartMain : MY_ENV_TEST2 : " + os.environ.get('MY_ENV_TEST2'))
        logging.info("CartMain : MY_ENV_TEST3 : " + os.environ.get('MY_ENV_TEST3'))
        logging.info("CartMain : MY_ENV_TEST4 : " + os.environ.get('MY_ENV_TEST4'))

        return self.cart

    def create(self, dataIn):
        self.cart.append(dataIn)
        return dataIn, 200