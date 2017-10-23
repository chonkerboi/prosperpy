class Position:
    def __init__(self, product, amount, price):
        self.product = product
        self.price = price
        self.amount = amount

    def __str__(self):
        return '{}<{}, amount: {:.2f}, price: {:.2f}>'.format(
            self.__class__.__name__, self.product, self.amount, self.price)
