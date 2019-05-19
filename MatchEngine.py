import numpy as np
import pandas as pd
pd.set_option('display.width', 280)


class MatchEngine(object):
    def __init__(self):
        self.md_path = "md_600000.csv"
        self.trade_path = "trade_600000.csv"
        self.md_events = None
        self.trade_events = None
        self.last_ts = None
        self.last_snapshot = None
        self.ts = None
        self.snapshot = None
        self.user_bid_orders = []
        self.user_ask_orders = []
        self.read_data()

    def place_order(self, user_order):
        if user_order.direction == 1:
            self.user_bid_orders.append(user_order)
            self.user_bid_orders.sort(key=lambda order: order.price, reverse=True)
        else:
            self.user_ask_orders.append(user_order)
            self.user_ask_orders.sort(key=lambda order: order.price, reverse=False)

    def reset(self):
        self.ts = self.md_events.index[0]
        self.last_ts = None
        self.user_bid_orders = []
        self.user_ask_orders = []

    def read_data(self):
        self.md_events = pd.read_csv(self.md_path, dtype={'DATE': np.str, 'TIME': np.str})
        self.md_events["DATE"] = self.md_events["DATE"] + self.md_events["TIME"]
        self.md_events['DATE'] = pd.to_datetime(self.md_events['DATE'])
        del self.md_events['TIME']
        self.md_events.drop_duplicates('DATE', inplace=True)
        self.md_events.set_index("DATE", inplace=True)
        self.ts = self.md_events.index[0]
        # print(self.md_events.head(10))

        self.trade_events = pd.read_csv(self.trade_path,
                                        dtype={'DATE': np.str, 'TIME': np.str})
        self.trade_events["DATE"] = self.trade_events["DATE"] + self.trade_events["TIME"]
        self.trade_events["DATE"] = self.trade_events["DATE"].map(lambda s: s[0:14])
        self.trade_events['DATE'] = pd.to_datetime(self.trade_events['DATE'])
        del self.trade_events['TIME']
        self.trade_events.set_index("DATE", inplace=True)
        # print(self.trade_events.head(10))

    def matchOrders(self, start_time=None, end_time=None):
        trades = []
        if start_time is None:
            start_time = self.ts
        else:
            self.last_ts=None

        if end_time is None:
            end_time = str(self.md_events.index[-1])
        print("match start time:"+str(start_time))
        print("match end time:"+str(end_time))
        sub_md_events = self.md_events[start_time:end_time]
        #print(sub_md_events)
        #print(self.trade_events[start_time:end_time])
        for i in range(len(sub_md_events)):
            self.ts = sub_md_events.index[i]
            #如果有keyerror 换成 self.snapshot = self.md_events.loc[str(self.ts)]
            self.snapshot = self.md_events[str(self.ts)].iloc[0]
            print(self.snapshot.to_frame().transpose())

            better_price = 99999999  # asume a very large price
            for bidorder in self.user_bid_orders:
                if self.last_ts is None:
                    # adjust order queue
                    for j in range(5):
                        price = self.snapshot[j + 10]
                        vol = self.snapshot[j + 15]
                        if price < better_price and price >= bidorder.price:
                            bidorder.before_qty += vol
                else:
                    # adjust order queue
                    last_pv_dict = {self.last_snapshot[i + 10]: self.last_snapshot[i + 15] for i in range(5)}
                    pv_dict = {self.snapshot[i + 10]: self.snapshot[i + 15] for i in range(5)}
                    sub_trade_events = self.trade_events[self.last_ts:self.ts].groupby('PRICE').sum()
                    trade_pv_dict = {price: sub_trade_events.loc[price][0] for price in sub_trade_events.index}
                    md_orders = {price: pv_dict.get(price, 0) - last_pv_dict.get(price, 0) + trade_pv_dict.get(price, 0)
                                 for price in set(last_pv_dict).union(pv_dict)}
                    for price, vol in md_orders.items():
                        if price < better_price and price >= bidorder.price:
                            # asume all added to behind
                            if vol > 0:
                                bidorder.after_qty += vol
                            # cancle order normally
                            elif vol < 0:
                                #print("about to cancel order in bidorder")
                                # cancle_before = vol * (
                                #         bidorder.before_qty / (
                                #             bidorder.before_qty + bidorder.after_qty + 0.000001)) // 100 * 100
                                # cancle_after = (vol - cancle_before) // 100 * 100

                                cancle_before = vol * (
                                        bidorder.before_qty / (
                                        bidorder.before_qty + bidorder.after_qty + 0.000001))
                                cancle_after = (vol - cancle_before)
                                bidorder.before_qty += cancle_before
                                bidorder.after_qty += cancle_after
                            else:
                                continue
                    # match by trade info
                    for price, vol in trade_pv_dict.items():
                        if price < better_price and price >= bidorder.price:
                            if vol <= bidorder.before_qty:
                                bidorder.before_qty -= vol
                            elif vol > bidorder.before_qty and vol <= bidorder.before_qty + bidorder.qty:
                                trades.append((bidorder.price, vol - bidorder.before_qty, self.ts))
                                bidorder.qty -= (vol - bidorder.before_qty)
                                bidorder.before_qty = 0
                            elif vol > bidorder.before_qty + bidorder.qty:
                                trades.append((bidorder.price, bidorder.qty, self.ts))
                                bidorder.after_qty -= (vol - bidorder.before_qty - bidorder.qty)
                                bidorder.before_qty = 0
                                bidorder.qty = 0
                better_price = bidorder.price

            better_price = -1  # asume a very small price
            for askorder in self.user_ask_orders:
                if self.last_ts is None:
                    # adjust order queue
                    for j in range(5):
                        price = self.snapshot[j]
                        vol = self.snapshot[j + 5]
                        if price > better_price and price <= askorder.price:
                            askorder.before_qty += vol
                else:
                    # adjust order queue
                    last_pv_dict = {self.last_snapshot[i]: self.last_snapshot[i + 5] for i in range(5)}
                    pv_dict = {self.snapshot[i]: self.snapshot[i + 5] for i in range(5)}
                    sub_trade_events = self.trade_events[self.last_ts:self.ts].groupby('PRICE').sum()
                    trade_pv_dict = {price: sub_trade_events.loc[price][0] for price in sub_trade_events.index}
                    md_orders = {price: pv_dict.get(price, 0) - last_pv_dict.get(price, 0) + trade_pv_dict.get(price, 0)
                                 for price in set(last_pv_dict).union(pv_dict)}
                    for price, vol in md_orders.items():
                        if price > better_price and price <= askorder.price:
                            if vol > 0:
                                askorder.after_qty += vol
                            # cancle order
                            elif vol < 0:
                                #print("about to cancel order in askorder")
                                askorder.before_qty += vol * (
                                        askorder.before_qty / (askorder.before_qty + askorder.after_qty + 0.000001))
                                askorder.after_qty += vol * (
                                        askorder.after_qty / (askorder.before_qty + askorder.after_qty + 0.000001))
                            else:
                                continue
                    # match by trade info
                    for price, vol in trade_pv_dict.items():
                        if price > better_price and price <= askorder.price:
                            if vol <= askorder.before_qty:
                                askorder.before_qty -= vol
                            elif vol > askorder.before_qty and vol <= askorder.before_qty + askorder.qty:
                                trades.append((askorder.price, vol - askorder.before_qty, self.ts))
                                askorder.qty -= (vol - askorder.before_qty)
                                askorder.before_qty = 0
                            elif vol > askorder.before_qty + askorder.qty:
                                trades.append((askorder.price, askorder.qty, self.ts))
                                askorder.after_qty -= (vol - askorder.before_qty - askorder.qty)
                                askorder.before_qty = 0
                                askorder.qty = 0
                better_price = askorder.price

            # remove full traded orders
            self.user_bid_orders = [order for order in self.user_bid_orders if order.qty > 0]
            self.user_ask_orders = [order for order in self.user_ask_orders if order.qty > 0]
            self.last_ts = self.ts
            self.last_snapshot = self.snapshot
            print("user_bid_orders"+str(self.user_bid_orders))
            print("user_ask_orders"+str(self.user_ask_orders))

        next_i = self.md_events.index.get_loc(self.last_ts)+1
        self.ts = self.md_events.index[next_i]
        return trades
