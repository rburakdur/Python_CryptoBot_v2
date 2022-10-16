import config
from binance import Client
import pandas as pd
import ta
import datetime as dt
import time
import requests
from numpy import exp
import winsound
############################################################################################


class botke():
    def __init__(self) -> None:
        self.main()

    symbols = ["SANDUSDT"]
    symbol = "SANDUSDT"
    interval = "1m"
    lookback = 40

    balance = 10
    leverage = 20

    ema_slow = 25
    ema_fast = 7

    in_position = False

    

    def telegram_bot_sendtext(self,bot_message):
        bot_token = "2098201745:AAFdIy7l6EDg_axpCAk68FfLBqoXqhQNSBU"
        bot_chatID = "-1001769230532"
        send_text = 'https://api.telegram.org/bot' + bot_token + \
            '/sendMessage?chat_id=' + bot_chatID + '&parse_mode=Markdown&text=' + bot_message
        response = requests.get(send_text)
        return response.json()

    def closed_position_excel(self, current_position):
        r = {"time": current_position[0], "side": current_position[1], "entry": current_position[2],
            "exit": current_position[3], "PNL": current_position[4],"ROE %": current_position[5], "balance": current_position[6]}
        df = pd.DataFrame([r])
        p = (f"{self.symbol}.xlsx")
        try:
            writer = pd.ExcelWriter(p, engine="openpyxl",mode="a", if_sheet_exists="replace")
            old = pd.read_excel(p)
            old = old.append(df)
            old.to_excel(writer, sheet_name="1", float_format="%.4f", index=False)
        except:
            writer = pd.ExcelWriter(p, engine="openpyxl",mode="w")
            df.to_excel(writer, sheet_name="1", float_format="%.4f", index=False)

        writer.sheets["1"].column_dimensions['A'].width = 20
        writer.save()
        writer.close()

    def main(self):
        while True:
            for symbol in self.symbols:
                self.symbol = symbol
                time.sleep(1)
                client = Client(config.api_key, config.secret_key,{"verify": True, "timeout": 10})
                client.futures_change_leverage(symbol=self.symbol, leverage=self.leverage)
                ###
                df = pd.DataFrame(client.futures_klines(symbol= self.symbol,interval = self.interval, limti = self.lookback))
                df = df.iloc[:, :6]
                df.columns = ["time","open","high","low","close","volume"]
                df = df.astype(float)
                df["ema_slow"] = ta.trend.ema_indicator(df.close,self.ema_slow)
                df["ema_fast"] = ta.trend.ema_indicator(df.close,self.ema_fast)
                p_info = client.futures_position_information(symbol = self.symbol)[0]["entryPrice"]
                currrent_price = df["close"][len(df.index)-1]
                ###
                ema_cross_up = (df["ema_fast"][len(df.index)-3] <= df["ema_slow"][len(df.index)-3]) and (df["ema_fast"][len(df.index)-2] > df["ema_slow"][len(df.index)-2])
                ema_cross_down = (df["ema_fast"][len(df.index)-3] >= df["ema_slow"][len(df.index)-3]) and (df["ema_fast"][len(df.index)-2] < df["ema_slow"][len(df.index)-2])
                ###
                def open_position(s):
                    winsound.Beep(1000,500)
                    side = ""
                    if s == "Long":
                        side = "BUY"
                    elif s == "Short": 
                        side = "SELL"
                    amount = int(self.balance/currrent_price)*self.leverage
                    client.futures_create_order(symbol = self.symbol, type = 'MARKET', side =side, quantity = amount)
                def close_position(s):
                    side = ""
                    pi = client.futures_position_information(symbol=self.symbol)[0]
                    entryPrice = pi["entryPrice"]
                    markPrice = pi["markPrice"]
                    pnl = pi["unRealizedProfit"]
                    isoleWallet = pi["isolatedWallet"]
                    roe = round((float(pnl)*100)/float(isoleWallet),2)
                    balance = client.futures_account_balance()[6]["balance"]
                    now = (dt.datetime.now().strftime("%d/%m/%Y %H:%M:%S"))
                    
                    ##
                    bs = (client.futures_position_information(symbol=self.symbol)[0]["positionAmt"])
                    if s == "Long":
                        side = "SELL"
                    elif s == "Short": 
                        side = "BUY"
                        bs = float(bs)*(-1)
                        bs = int(bs)
                    c = [now,side,entryPrice,markPrice,pnl,roe,balance]
                    self.closed_position_excel(c)
                    self.telegram_bot_sendtext(f"Symbol   :   {self.symbol}\nProfit   :   {c[4]}\nROE   :   {roe} %\nBalance  :   {c[6]}\n{s} closed at  {c[3]}\n{c[0]}")
                    client.futures_create_order(symbol=self.symbol,
                                                type="MARKET",
                                                side=side,
                                                quantity=bs,
                                                reduceOnly="true")
                ###
                if p_info == "0.0":                            
                    if ema_cross_up:
                        open_position("Long")
                    elif ema_cross_down:
                        open_position("Short")
                    else:                       
                        print(f"Pozisyon aranıyor... {str(currrent_price)}")

                else:
                    s = float(client.futures_position_information(symbol=self.symbol)[0]["positionAmt"])
                    ww = client.futures_position_information(symbol=self.symbol)[0]["unRealizedProfit"]
                    if (s > 0):
                        if ema_cross_down:
                            close_position("Long")
                        else:
                            print("in long position...  ",ww)
                    elif (s < 0):
                        if ema_cross_up:
                            close_position("Short")
                        else:                        
                            print("in short position...  ",ww)
            
            
botke()
