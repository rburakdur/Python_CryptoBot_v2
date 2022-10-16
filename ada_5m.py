import config
from binance import Client
import pandas as pd


def futures_taker_buysell_volumes(**params):
    return Client()._request_futures_data_api('get', 'takerlongshortRatio', data=params)


def connect():
    client = Client(config.api_key, config.secret_key,
                    {"verify": True, "timeout": 10})

    #futures_taker_buysell_volume(symbol="BTCUSDT", period="15m")
    a = futures_taker_buysell_volumes(
        symbol="OCEANUSDT", period="5m")
    df = pd.DataFrame(a)
    sell = float(df.loc[29]["sellVol"])
    buy = float(df.loc[29]["buyVol"])
    sellP = round(sell*100/(sell+buy), 2)
    buyP = round(buy*100/(sell+buy), 2)

    print("short %", sellP, "long %", buyP)
    print(df)


# while True:
    # #df = pd.DataFrame(connect().futures_klines(symbol=symbol, interval=interval, limit=lookback))
    # df = pd.DataFrame
    # df = df.iloc[:, :6]
    # df.columns = ["time", "open", "high", "low", "close", "volume"]
    # df = df.astype(float)

connect()
