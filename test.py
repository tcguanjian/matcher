import numpy as np
import pandas as pd
from MatchEngine import MatchEngine
from Order import Order

#test engine
engine = MatchEngine()

order = Order(qty=10000,direction=1,price=10.82)
order2 = Order(qty=10000,direction=2,price=10.84)
engine.place_order(order)
engine.place_order(order2)
trades = engine.matchOrders('2018-12-13 13:59:39','2018-12-13 13:59:48')
print(trades)
trades = engine.matchOrders(end_time='2018-12-13 14:05:48')
print(trades)

# engine.reset()
# order = Order(qty=10000,direction=1,price=10.82)
# engine.place_order(order)
# trades = engine.matchOrders('2018-12-13 13:59:39','2018-12-13 13:59:48')
# print(trades)
# print(engine.user_bid_orders)
# print(engine.user_ask_orders)
# trades = engine.matchOrders(end_time='2018-12-13 14:01:48')
# print(trades)
# print(engine.user_bid_orders)
# print(engine.user_ask_orders)


# engine.reset()
# order = Order(qty=10000,direction=1,price=10.82)
# engine.place_order(order)
# trades = engine.matchOrders('2018-12-13 13:59:39','2018-12-13 14:59:48')
# print(trades)


# for i in range(1000000):
#     print(i)
#     engine.reset()
#     order = Order(qty=1000, direction=1, price=10.82)
#     order2 = Order(qty=10000, direction=2, price=10.84)
#     engine.place_order(order)
#     engine.place_order(order2)
#     trades = engine.matchOrders('2018-12-13 13:59:39', '2018-12-13 13:59:48')
#     #print(trades)
#
#     trades = engine.matchOrders(end_time='2018-12-13 14:05:48')
#     #print(trades)