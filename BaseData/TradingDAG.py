class TradingDAG:
    def __init__(self, name):
        self.name = name
        self.base_neighbors = []
        self.quote_neighbors = []