class Position:
    def __init__(self, product, amount, price):
        self.product = product
        self.price = price
        self.amount = amount

    def __str__(self):
        return '{}<{} amount: {}, price: {}>'.format(self.__class__.__name__, self.product, self.amount, self.price)
