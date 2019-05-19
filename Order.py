class Order(object):
    def __init__(self,price=0,qty=0,before_qty=0,after_qty=0,direction=1):
        self.price = price
        self.qty=qty
        self.before_qty=before_qty
        self.after_qty=after_qty
        self.direction=direction # 1 for buy, 2 for sell

    def __str__(self):
        return "\"price:"+str(self.price)+" qty:"+str(self.qty)+" before_qty:"+str(self.before_qty)+" after_qty:"+str(self.after_qty)+" direction:"+str(self.direction)+"\"";

    def __repr__(self):
        return str(self)