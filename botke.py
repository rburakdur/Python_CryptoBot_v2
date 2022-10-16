import config
from binance import Client
import pandas as pd
import ta
import datetime as dt
import time
import requests
from numpy import exp


class lydesa():
    def __init__(self) -> None:
        self.main()

    symbols = ["SANDUSDT", "ETHUSDT", "GALAUSDT",
               "BTCUSDT", "SUSHIUSDT", "LINKUSDT"]
    #symbols = ["SANDUSDT"]
    interval = "1m"
    lookback = 40

    wallet = 100

    ema_slow = 8
    ema_fast = 5

    roe = 0

    def main(self):
        while True:
            time.sleep(59)
            for symbol in self.symbols:
                try:

                    client = Client(config.api_key, config.secret_key)
                    # , {"verify": True, "timeout": 10}

                    df = pd.DataFrame(client.futures_klines(
                        symbol=symbol, interval=self.interval, limit=self.lookback))
                    df = df.iloc[:, :6]
                    df.columns = ["time", "open",
                                  "high", "low", "close", "volume"]
                    df.astype(float)
                    currrent_price = df["close"][len(df.index)-1]
                    df["ema_slow"] = ta.trend.ema_indicator(
                        df.close, self.ema_slow)
                    df["ema_fast"] = ta.trend.ema_indicator(
                        df.close, self.ema_fast)
                    df["macd"] = ta.trend.MACD(df.close).macd_diff()
                    df["symbol"] = symbol
                    # in_position check from positions.csv
                    positions = pd.read_csv("positions.csv")
                    p = len(positions[positions.symbol == symbol])
                    ###
                    ema_cross_up = (df["ema_fast"][len(df.index)-3] <= df["ema_slow"][len(df.index)-3]) and (
                        df["ema_fast"][len(df.index)-2] > df["ema_slow"][len(df.index)-2])
                    ema_cross_down = (df["ema_fast"][len(df.index)-3] >= df["ema_slow"][len(df.index)-3]) and (
                        df["ema_fast"][len(df.index)-2] < df["ema_slow"][len(df.index)-2])
                    macd_diff_decrase = (
                        df["macd"][len(df.index)-3] > df["macd"][len(df.index)-2])
                    macd_diff_incase = (
                        df["macd"][len(df.index)-3] < df["macd"][len(df.index)-2])
                    ###

                    def open_positions(a):
                        c = {"symbol": symbol, "side": a,
                             "entryPrice": currrent_price}
                        c = pd.DataFrame([c])
                        c = pd.concat([positions, c], axis=0,
                                      ignore_index=True)
                        c.to_csv("positions.csv", index=False)

                    def close_position(a):
                        pos = positions[positions.symbol == symbol]
                        now = (dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                        entryPrice = float(pos["entryPrice"])
                        side = a
                        markPrice = float(currrent_price)
                        if side == "Long":
                            self.roe = round((markPrice-entryPrice)
                                             * 100/entryPrice, 3)
                        elif side == "Short":
                            self.roe = round(
                                (entryPrice - markPrice)*100/entryPrice, 3)
                        f = {"time": now, "symbol": symbol, "side": side, "entryPrice": entryPrice,
                             "markPrice": markPrice, "ROE %": self.roe}
                        f = pd.DataFrame([f])
                        cp = pd.read_csv("closed_positions.csv")
                        f = pd.concat([cp, f], ignore_index=True, axis=0)
                        f.to_csv("closed_positions.csv",
                                 index=False)

                        pp = positions.loc[positions["symbol"] != symbol]
                        pp.to_csv("positions.csv", index=False)

                    if p == 0:
                        if ema_cross_up:
                            open_positions("long")
                        elif ema_cross_down:
                            open_positions("short")
                        else:
                            print(
                                f"Pozisyon aranıyor... {symbol} - {str(currrent_price)}")
                    else:
                        cc = positions[positions.symbol == symbol]
                        if (cc["side"] == "long").bool():
                            if ema_cross_down:
                                close_position("Long")
                            else:
                                print("in long position... ", symbol)
                        elif (cc["side"] == "short").bool():
                            if ema_cross_up:
                                close_position("Short")
                            else:
                                print("in short position... ", symbol)
                except:
                    print("başaramadık abi...")
                    client.close_connection()
                    client = Client(config.api_key, config.secret_key)
                    pass


if __name__ == "__main__":
    lydesa()
