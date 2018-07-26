import calendar
import datetime
import fcoin
import networkx as nx
import threading
import timeit
from BaseData.TradingDAG import TradingDAG
from FcoinData.FCoinConfig import FCoinConfig


class FCoinTradingData:
    def __init__(self):
        self.trading_dag = {}
        self.api = fcoin.authorize(FCoinConfig.public_key, FCoinConfig.secret_key)
        self.trading_pairs_list = []

    def get_time_stamp(self):
        time = datetime.datetime.utcnow()
        return calendar.timegm(time.timetuple())

    def get_trading_pairs(self):
        return self.api.symbols()
        # list = api.symbols()
        # self.trading_pairs_list = list
        # for idx, row in list.iterrows():
        #     print(row['name'])

    def get_trading_data_by_pair(self, symbol):
        return self.api.get_ticker(symbol)

    def get_trading_dag(self, pairs_list):
        if len(self.trading_dag) > 0:
            return self.trading_dag
        # create graph
        self.trading_dag = nx.DiGraph()
        # build DAG for coins
        for idx, row in pairs_list.iterrows():
            base = row['base_currency']
            quote = row['quote_currency']
            if base not in self.trading_dag:
                self.trading_dag.add_node(base)
            if quote not in self.trading_dag:
                self.trading_dag.add_node(quote)
            self.trading_dag.add_weighted_edges_from([(base, quote, -0.01)])
            self.trading_dag.add_weighted_edges_from([(quote, base, -0.01)])
        return self.trading_dag

    def update_all_tickers(self, pairs_list):
        thread_list = []
        for idx, row in pairs_list.iterrows():
            base = row['base_currency']
            quote = row['quote_currency']
            thread_list.append(UpdateTickerThread(base + quote, self.trading_dag, base, quote))
            thread_list[len(thread_list) - 1].start()
        return thread_list

    def exec_market_order(self, pair, trade_dir,  quantity):
        return self.api.create_order(symbol=pair,side = trade_dir, type = 'market', amount = quantity)

    def exec_limit_order(self, pair, trade_dir, price,  quantity):
        return self.api.create_order(symbol=pair,side = trade_dir, type = 'market' ,price=str(price), amount = quantity)

    def get_order_info(self, order):
        if isinstance(order, str):
            if "market order is disabled" in str(order):
                a = {}
                a['data'] = "MD"
                return a
        elif self.get_order_info(order) is not None:
            return self.get_order_info(order)['data'];
        return None

    def get_order_state(self, order):
        return order['state']

    def get_order_amount(self, order):
        return order['amount']

    def get_balance(self):
        return self.api.get_balance()

    def get_ticker(self, pair):
        ticker_data = self.api.get_ticker(pair)['data']['ticker']

class UpdateTickerThread(threading.Thread):
    def __init__(self, threadID, trading_dag, base, quote):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.trading_dag = trading_dag
        self.base = base
        self.quote = quote

    def run(self):
        api = fcoin.authorize(FCoinConfig.public_key, FCoinConfig.secret_key);
        try:
            ticker_data = api.get_ticker(self.base + self.quote)['data']['ticker']
        except Exception:
            ticker_data = api.get_ticker(self.base + self.quote)['data']['ticker']

        self.trading_dag.remove_edge(self.base, self.quote)
        self.trading_dag.add_weighted_edges_from([(self.base, self.quote, ticker_data[2])])
        self.trading_dag[self.base][self.quote]['size'] = ticker_data[3]

        self.trading_dag.remove_edge(self.quote, self.base)
        self.trading_dag.add_weighted_edges_from([(self.quote, self.base, 1 / ticker_data[4])])
        self.trading_dag[self.quote][self.base]['size'] = ticker_data[5]
        # print("match %s to %s, value %8.9f and reverse value %8.9f original: %f" % (self.base, self.quote, \
        #                                                                                         ticker_data[2],
        #                                                                                         1 / ticker_data[4], \
        #                                                                                         ticker_data[4]))
