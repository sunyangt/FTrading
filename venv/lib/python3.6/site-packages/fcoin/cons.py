SERVER = 'api.fcoin.com'
PORT = 80
HT= 'https://%s/v2/'
HTMRK = 'https://%s/v2/market/'
HTPBL = 'https://%s/v2/public/'
HTORD = 'https://%s/v2/orders/'
HTACT = 'https://%s/v2/accounts/'
WS = 'wss://%S/v2/ws/'

ST = 'server-time'
SYMBOLS = 'symbols'
CURRENCY = 'currencies'
TICKER = 'ticker/%s'

POST = 'POST'
GET = 'GET'

KDATA = 'candles/%s/%s'
KDATA_COLUMNS = ['id', 'open', 'high', 'low', 'close', 'count', 'base_vol', 'quote_vol', 'seq']
KDATA_REAL_COL = ['datetime', 'open', 'high', 'low', 'close', 'count', 'base_vol', 'quote_vol', 'seq']