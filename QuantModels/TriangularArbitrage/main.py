from FcoinData.FCoinConfig import FCoinConfig
from FcoinData.FCoinTradingData import FCoinTradingData
from threading import Thread
import timeit
import time
import traceback

max_profit = -1
max_profit_path = ''
update_time = timeit.default_timer() - 1000
exec_state = 0
trading_data = FCoinTradingData()
pairs = None


def main():
    global trading_data, pairs
    pairs = trading_data.get_trading_pairs()
    dag = trading_data.get_trading_dag(pairs)
    counter = 0

    while (True):
        start_time = timeit.default_timer()
        thread_list = trading_data.update_all_tickers(pairs)
        for th in thread_list:
            th.join(3)
        print("finish updating data")
        get_diff_list('eth', dag, 2, 2, 'eth', 'eth', 1)
        stop_time = timeit.default_timer()
        print("itr %d takes %f to finish." % (counter, stop_time - start_time))
        counter += 1



def trade():
    global update_time, max_profit, exec_state, max_profit_path, trading_data, pairs
    while (True):
        try:
            if timeit.default_timer() - update_time < 1.5 \
                    and max_profit > FCoinConfig.exchange_charge * FCoinConfig.execute_multiple * 100:
                exec_state = 1
                print("trading start with" + max_profit_path)
                amount = FCoinConfig.limit_eth;
                path_list = max_profit_path.split('-')
                for idx in range(1, len(path_list)):
                    dir_from = path_list[idx - 1]
                    dir_to = path_list[idx]
                    base = ''
                    quote = ''
                    for idx, row in pairs.iterrows():
                        if row['name'] == (dir_from + dir_to) or row['name'] == (dir_to + dir_from):
                            base = row['base_currency']
                            quote = row['quote_currency']
                    order_id = ''
                    if base == dir_from:
                        order_id = trading_data.exec_order(base + quote, 'sell', 'market', amount)
                    else:
                        order_id = trading_data.exec_order(base + quote, 'buy', 'market', amount)

                    if order_id is not None:
                        order_info = trading_data.get_order_info(order_id)
                    else:
                        print("order does not success ")

                exec_state = 0
                max_profit = -1
            time.sleep(0.1)
        except Exception as ex:
            print(traceback.format_exc())


bal_lock = Thread.Lock()
bal = {}
tract_done = False
amount_list = []

def trading(dir_from, dir_to, tid, limit):
    global amount_list, bal,bal_lock, trading_data
    while (True):
        balance = 0
        with bal_lock:
            balance = bal[dir_from]
        base = ''
        quote = ''
        for idx, row in pairs.iterrows():
            if row['name'] == (dir_from + dir_to) or row['name'] == (dir_to + dir_from):
                base = row['base_currency']
                quote = row['quote_currency']
        order_id = ''
        # if not ft coin try market order first
        if base == dir_from and 'ft' not in dir_from+dir_to:
            order_id = trading_data.exec_market_order(base + quote, 'sell', min(limit, balance))
        elif 'ft' not in dir_from+dir_to:
            order_id = trading_data.exec_market_order(base + quote, 'buy', 'market', min(limit, balance))
        # process ft coin
        if 'ft' in dir_from+dir_to:
            trading_data.
            if base == dir_from:
                order_id = trading_data.exec_limit_order(base + quote, 'sell', 'market', min(limit, balance))
            else:
                order_id = trading_data.exec_limit_order(base + quote, 'buy', 'market', min(limit, balance))

        if order_id is not None:
            order_info = trading_data.get_order_info(order_id)
        else:
            print("order does not success ")


def update_bal():
    global bal, tract_done
    while(not tract_done):
        with bal_lock:
            bal = trading_data.get_balance();
        time.sleep(0.2)


def get_diff_list(symbol, dag, deep, origin_deep, origin_syl, path, cur_value):
    if deep < 0:
        if cur_value > 1.0:
            global update_time
            profit = (cur_value - 1) * 100
            print("path %s after_value: %8.8f, cur_profit: %8.8f %%" % (path, cur_value, profit))
            if profit > FCoinConfig.exchange_charge * FCoinConfig.execute_multiple \
                    and exec_state == 0 and timeit.default_timer() - update_time > 20:
                global max_profit_path, max_profit
                max_profit_path = path
                max_profit = profit
                update_time = timeit.default_timer()

        # else:
        #     print("No Profit path %s curvalue %8.8f curprofit: %8.8f" % (path, cur_value, (cur_value - 1) * 100))
        return 0;
    # recurisive to next deep
    neighbors = dag.edges([symbol])
    for coin in neighbors:
        if (symbol != origin_syl and coin[0] != origin_syl and coin[1] != origin_syl and deep > 0) \
                or (symbol == origin_syl and deep == origin_deep) \
                or (deep == 0 and ((coin[0] == origin_syl) ^ (coin[1] == origin_syl))):
            target = ''
            exchange_rate = -1
            size = -1
            if coin[1] != symbol:
                target = coin[1]
                exchange_rate = dag[symbol][target]['weight']
                if dag[symbol][target]['size'] is not None:
                    size = dag[symbol][target]['size']
            else:
                target = coin[0]
                exchange_rate = dag[target][symbol]['weight']
                if dag[target][symbol]['size'] is not None:
                    size = dag[target][symbol]['size']
            value = cur_value * exchange_rate * (1 - FCoinConfig.exchange_charge)
            get_diff_list(target, dag, deep - 1, origin_deep, origin_syl, path + "-" + target, value)


if __name__ == "__main__":
    thread = Thread(target=trade)
    thread.setDaemon(True)
    thread.start()
    main()
