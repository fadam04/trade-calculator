import traceback
import tkinter as tk
from tkinter import messagebox
import math
from pybit.unified_trading import HTTP
import threading
from tkinter import ttk
import pyperclip
from decimal import Decimal, getcontext
from tkinter import PhotoImage
from PIL import Image, ImageTk
import numpy as np
import pandas as pd
import ta
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# Beállítjuk a kontextust, hogy hány tizedesjegyig számoljon
getcontext().prec = 10

# Alapértelmezett értékek
currency = '$'
risk_percent = 2
price=1000
data = []
sma_length=200
length=14

def auto_add_widget(parent, widget, row, col, sticky="w", padx=5, pady=5):
    widget.grid(row=row, column=col, sticky=sticky, padx=padx, pady=pady)

def get_data():
 global data
 try:
    session = HTTP(testnet=False )
    symbol = coin_entry.get().upper()
    time=time_var.get()
    
    response=(session.get_mark_price_kline(
    category="linear",
    symbol=symbol+"USDT",
    interval=time,))

    data=response["result"]["list"]
    return data
 except Exception as e:
   messagebox.showerror("Hiba", f"Árfolyam lekérése sikertelen: {str(e)}")

def data_convert():
    global df
    get_data()
    df = pd.DataFrame(data)
    
    df.columns = ['timestamp', 'open', 'high', 'low', 'close']
    df['open'] = pd.to_numeric(df['open'])
    df['high'] = pd.to_numeric(df['high'])
    df['low'] = pd.to_numeric(df['low'])
    df['close'] = pd.to_numeric(df['close'])
    df['timestamp'] = pd.to_numeric(df['timestamp'])
    try:
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    except Exception as e:
        messagebox.showerror("Hiba", f"Dátum konvertálása sikertelen: {e}")
    
    df = df.sort_values(by='timestamp', ascending=True) 
    df.set_index('timestamp', inplace=True)
    return df
def get_data_for_chart():
    df=data_convert()
    df['RSI'] = ta.momentum.RSIIndicator(close=df['close'], window=14).rsi()
    df['Stoch RSI'] = ta.momentum.stochrsi(close=df['close'], window=14)
    df['K'] = ta.momentum.stochrsi_k(close=df['close'], window=14, smooth1=3, smooth2=3)
    df['D'] = ta.momentum.stochrsi_d(close=df['close'], window=14, smooth1=3, smooth2=3)
    df['ATR'] = ta.volatility.AverageTrueRange(high=df['high'], low=df['low'], close=df['close'], window=14).average_true_range()
    df['SMA'] = df['close'].rolling(window=sma_length, min_periods=1).mean()
    df['SMA'] = df['SMA'].bfill()  # Kitöltés a következő érvényes értékkel
    df['MACD'] = ta.trend.MACD(close=df['close']).macd()
    df['MACD Signal'] = ta.trend.MACD(close=df['close']).macd_signal()
    df['Bollinger High'] = ta.volatility.BollingerBands(close=df['close']).bollinger_hband()
    df['Bollinger Low'] = ta.volatility.BollingerBands(close=df['close']).bollinger_lband()
    
    return df
def get_sma(sma_length):
    """
    Egyszerű mozgóátlag (SMA) számítása.
    :param data: Az adatsor (lista vagy numpy array).
    :param period: A mozgóátlag periódusa (N).
    :return: Az SMA értékek listája.
    """
    period = int(sma_length)
    sma = []
    
    for i in range(len(data) - period + 1):
        window =data[i:i + period]  # Az N hosszú részlet
        average = sum([Decimal(item[4]) for item in window]) / period
        sma.append(average)
    smalast=float(sma[len(sma)-1])
    sma_entry.delete(0, tk.END)
    sma_entry.insert(0, f"{smalast}")
    return smalast








def calculate_rsi(data,period=14):
    
    gains = []
    losses = []
    rsi_values = []
   
    # Záró árak közötti változások kiszámítása
    for i in range(1, len(data)):
        change = data[i] - data[i - 1]
        if change > 0:
            gains.append(change)
            losses.append(0)
        else:
            gains.append(0)
            losses.append(abs(change))

    # Átlagos nyereség és veszteség kiszámítása
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period

    # Mozgó átlag (további időszakok)
    for i in range(period, len(data)):
        change = data[i] - data[i - 1]
        gain = max(change, 0)
        loss = abs(min(change, 0))

        avg_gain = (avg_gain * (period - 1) + gain) / period
        avg_loss = (avg_loss * (period - 1) + loss) / period
        if avg_loss == 0:
            rsi_values.append(100)
        else:
            rs = avg_gain / avg_loss
            rsi_values.append(100 - (100 / (1 + rs)))
    
    # RSI számítása
    if avg_loss == 0:
        return 100  # Ha nincs veszteség, az RSI 100
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
  
    return rsi_values

def get_rsi():
   
   
    close_prices = [float(entry[4]) for entry in data]
    close_prices.reverse()
    # RSI számítása
    period = int(length)
    rsi_values = calculate_rsi(close_prices,period=period)
    rsi_entry.delete(0, tk.END)
    rsi_entry.insert(0, f"{rsi_values[0]:.2f}")
    return rsi_values


def calculate_stoch_rsi(rsi_values, period=14,stoch_period=14):
    # Először kiszámítjuk az RSI-t
    
    
    

       
    rsi_window=rsi_values[-14:]
    rsi_min = min(rsi_window)
    rsi_max = max(rsi_window)
    
        # StochRSI normalizált értéke
    if rsi_max - rsi_min == 0:
        stoch_rsi = 0  # Ha nincs változás az RSI-ben
    else:
        stoch_rsi = (rsi_values[-1] - rsi_min) / (rsi_max - rsi_min)
    
    return stoch_rsi








def get_stoch_rsi():
    
    period=int(length)
    
   
    rsi_values=get_rsi()
    
    stoch_rsi=calculate_stoch_rsi(rsi_values,period=period,stoch_period=14)
    stoch_rsi=stoch_rsi*100
    
    stoch_rsi_entry.delete(0, tk.END)
    
    stoch_rsi_entry.insert(0,f"{stoch_rsi:.2f}")
    return stoch_rsi


def show_selection():
    selection = option_var.get()  # A kiválasztott elem lekérése
    coin_entry.delete(0, tk.END)
    coin_entry.insert(0, f"{selection}")  
options = ["Btc", "Eth", "Ondo", "Sol","Xrp","Imx","Render"]




#atr kalkulacio
def get_atr():#symbol,time,lenght
  try:
    
    lenght=int(length)
    open_prices=[]
    high_prices=[]
    low_prices=[]
    close_prices=[]
    Trs=[]
    
    for x in range(int(lenght)):
     open_prices.append(float((data[x][1])))
     high_prices.append(float((data[x][2])))
     low_prices.append(float((data[x][3])))
     close_prices.append(float((data[x][4])))
     Trs.append(max(high_prices[x] - low_prices[x], abs(high_prices[x] - close_prices[x]), abs(low_prices[x] - close_prices[x])))


    atr=(sum(Trs))/len(Trs)
    atr_entry.delete(0, tk.END)
    atr_entry.insert(0, f"{atr}")
    return atr
  except Exception as e:
     messagebox.showerror("Hiba", f" atr lekérése sikertelen: {e}")
def get_highest_price():
 try:    
    
    lenght=int(length)
    high_prices=[]
    for x in range(int(lenght)):
     
     high_prices.append(float((data[x][2])))
    highest=max(high_prices)
    tp_custom_entry.delete(0, tk.END)
    tp_custom_entry.insert(0, f"{highest}")  
    return highest          
 except Exception as e:
        messagebox.showerror("Hiba", f" Highest price  sikertelen a: {e}")
def get_lowest_price():
 try:   
    
    lenght=int(length)
    low_prices=[]
    for x in range(int(lenght)):
     low_prices.append(float((data[x][3])))
    lowest=min(low_prices)
    tp_custom_entry.delete(0, tk.END)
    tp_custom_entry.insert(0, f"{lowest}")
    return lowest
 except Exception as e:
        messagebox.showerror("Hiba", f" lowest price sikertelen: {e}")
#árfolyam lekérdeyése
        
        
def get_price():
 try:            
     last_price = data[0][4]   
     price_entry.delete(0, tk.END)
     price_entry.insert(0, f"{last_price}")                
 except Exception as e:
        messagebox.showerror("Hiba", f" get price sikertelen: {e}")




def get_all_data():
    def worker():
        try:
            get_data()  # Fetch data
            root.after(0,data_convert)
            root.after(0, get_rsi)  # Safely update RSI
            root.after(0,get_stoch_rsi)
            root.after(0, get_atr)  # Safely update ATR
            root.after(0, get_price)  # Safely update Price
            root.after(0, get_sma,sma_length)  # Safely update SMA
            
            
        except Exception as e:
         root.after(0,   messagebox.showerror,"Hiba", f"Hiba történt: {e}")
    threading.Thread(target=worker).start()


# Számítások függvényei
def calculate_trade_details_long(total_balance, current_price, atr, take_profit_custom, risk_percent, currency,custom2):
    
    
    
    
    
    if custom2 is True:
        stop_loss = stop_lost_custom_entry.get()
        stop_loss=Decimal(stop_loss)
    else:
        stop_loss = round(current_price - 3 * atr,2)
    take_profit = round(current_price + atr * 6,4)
    profit_potential = (round(take_profit_custom / current_price * 100)-100)
    loss_potential = round(100 - (stop_loss / current_price) * 100)
    max_loss = (total_balance * risk_percent / 100)
    trade_size = round((max_loss / loss_potential) * 100)
    
    
    
    a = abs(Decimal(current_price) -Decimal (take_profit_custom))
    b = abs(Decimal(stop_loss) -Decimal( current_price))
    rrr=a/b
    if abs(a) > 0 and abs(b) > 0:
         a_int = int(a * 10000)  # A pontosítás érdekében szorozzuk meg
         b_int = int(b * 10000)
        
         gcd = math.gcd(a_int,b_int)
         ratio = f'{a_int  // gcd}:{b_int // gcd}'
    else:
     ratio = "Nem számolható (osztás nullával)"

    return stop_loss, take_profit, profit_potential, loss_potential, max_loss, trade_size, ratio, a, b,rrr

def calculate_trade_details_short(total_balance, current_price, atr, take_profit_custom, risk_percent, currency,custom2):
    
    if custom2 is True:
        stop_loss = stop_lost_custom_entry.get()
        stop_loss=float(stop_loss)
    else:
        stop_loss = round(current_price + 3 * atr,4)
    take_profit = round(current_price - atr * 6,4)
    profit_potential = (round((current_price - take_profit_custom) / current_price * 100))
    loss_potential = round((stop_loss - current_price) / current_price * 100)
    max_loss = (total_balance * risk_percent / 100)
    trade_size = round((max_loss / loss_potential) * 100)
  
    a = abs(Decimal(current_price) -Decimal (take_profit_custom))
    b = abs(Decimal(stop_loss) -Decimal (current_price))
    rrr=a/b
    if abs(a) > 0 and abs(b) > 0:
         a_int = int(a * 10000)  # A pontosítás érdekében szorozzuk meg
         b_int = int(b * 10000)
        
         gcd = math.gcd(a_int,b_int)
         ratio = f'{a_int  // gcd}:{b_int // gcd}'
    
    
    
    else:
     ratio = "Nem számolható (osztás nullával)"

    return stop_loss, take_profit, profit_potential, loss_potential, max_loss, trade_size, ratio, a, b,rrr

# Eredmény kiíró függvény
def calculate_trade(order_type):
    get_data()
    try:
        total_balance = float(balance_entry.get())
        current_price = float(price_entry.get())
        atr = float(atr_entry.get())
        take_profit_custom = float(tp_custom_entry.get())
        risk_percent = int(risk_entry.get())
        currency = currency_var.get()
        smalast=float(sma_entry.get())
        if smalast>current_price:
            goodsma= False
        else: goodsma= True    
        
        if order_type == 'LONG':
           custom = custom_var_tp.get()
           custom2=custom_var_sl.get()
           if custom is False: 
            highest= get_highest_price()
            take_profit_custom = float(highest)
           
           stop_loss, take_profit, profit_potential, loss_potential, max_loss, trade_size, ratio, a, b,rrr = calculate_trade_details_long(
                total_balance, current_price, atr, take_profit_custom, risk_percent, currency,custom2)
           
           if custom2 is True:
               stop_loss=stop_lost_custom_entry.get()
               stop_loss=float(stop_loss)
               stop_loss
           else: stop_lost_custom_entry.insert(0,stop_loss)
           if take_profit_custom < current_price:
              messagebox.showerror("Hiba", "A take profit nem lehet kisebb a jelenlegi árnál Long pozicióba!")
              return
        elif order_type == 'SHORT':
            custom = custom_var_tp.get()
            custom2=custom_var_sl.get()
            if custom is False:
              lowest=get_lowest_price()
              take_profit_custom=float(lowest)
              
            stop_loss, take_profit, profit_potential, loss_potential, max_loss, trade_size, ratio, a, b,rrr = calculate_trade_details_short(
                total_balance, current_price, atr, take_profit_custom, risk_percent, currency,custom2)
            
            if custom2 is True:
               stop_loss=stop_lost_custom_entry.get()
               stop_loss=float(stop_loss)
               stop_loss
            else: stop_lost_custom_entry.insert(0,stop_loss)
            
            
            
            if take_profit_custom > current_price:
              messagebox.showerror("Hiba", "A take profit nem lehet nagyobb a jelenlegi árnál short pozicióba!")
              return

     
        
    
        # Eredmények megjelenítése
        result_text = f"""
        Stop loss helye: {stop_loss}{currency}
        Ideális Take profit 3X hez : {take_profit}{currency}
        Lehetséges nyereség: {profit_potential}%
        Lehetséges veszteség: {loss_potential}%
        Trade mérete: {trade_size}{currency}
        A megadott take profit hellyel a reward-risk ratio = {ratio}
       
        """
        result_text_widget.config(state=tk.NORMAL)
        result_text_widget.delete("1.0", tk.END)
        result_text_widget.insert(tk.END, f"Stop loss helye: {stop_loss}{currency}\n", "info")
        result_text_widget.insert(tk.END, f"Ideális Take profit 2X  hez: {take_profit}{currency}\n", "info")
        result_text_widget.insert(tk.END, f"Lehetséges nyereség: +{profit_potential}%\n", "info")  
        result_text_widget.insert(tk.END, f"Lehetséges veszteség: {max_loss}{currency}\n","bad")
        
        result_text_widget.insert(tk.END, f"Trade mérete: {trade_size}{currency}\n", "info")
        result_text_widget.insert(tk.END, f"RRR:{rrr}\n", "info")
        
       
        
        if goodsma is True:
          sma_result="A sma > mint  az ár, ez jó long poziciohoz"
        else:
         sma_result="A sma < mint az  ár, ez jó short poziciohoz"
        
        result_text_widget.insert(tk.END, f"{sma_result}\n","info")
        rsi=float(rsi_entry.get())
        if rsi>70:
            rsi_result="Overbought",
        elif rsi<30:
            rsi_result="Oversold",
        else:
            rsi_result="Neutral",
            
        result_text_widget.insert(tk.END, f"Rsi:{rsi_result}\n","info")
        szin = "neutral"
        if a == 0 or b == 0:
          result_text += "\n Hiba: Az arány nem számítható (osztás nullával)."
        else:
         risk_reward_ratio = b / a
         if risk_reward_ratio < 1/2:
          result_text_widget.insert(tk.END, "Jó trade: a nyereség kétszer több\n", "good")
          szin="good"
         elif risk_reward_ratio <= 1:
          result_text_widget.insert(tk.END, "Elfogadható trade: a nyereség kisebb, de nem rossz\n", "neutral")
          szin="neutral"
         else:
          result_text_widget.insert(tk.END, "Rossz trade: a veszteség nagyobb, mint a nyereség\n", "bad")
          szin="bad"
       
        
        result_text_widget.insert(tk.END,f"Ratio reward:risk: "+ratio+ "\n",szin)
        result_text_widget.config(state=tk.DISABLED)
    except ValueError:
        messagebox.showerror("Hiba", "Kérjük, érvényes számértékeket adjon meg!")




#Az összes gyerekelemet balra igazítja egy adott szülő widgetben.   

# A Take profit értékének másolása a vágólapra
def copy_to_clipboard(entry_field):
    clipboard_data = entry_field.get()
    root.clipboard_clear()
    root.clipboard_append(clipboard_data)
    root.update()
# A Take profit értékének másolása a vágólapra






  
LANGUAGES = {
    "Magyar": {
        "title": "Trade Kalkulátor",
        "balance": "Teljes egyenleg:",
        "coin": "Coin:",
        "timeframe": "Időkeret:",
        "length": "Hossz:",
        "price": "Jelenlegi Ár:",
        "sma": "SMA:",
        "rsi": "RSI:",
        "atr": "ATR:",
        "tp": "Take Profit:",
        "sl": "Stop Loss:",
        "calculate_long": "LONG Számítása",
        "calculate_short": "SHORT Számítása",
        "copy_tp": "TP Másolása",
        "copy_sl": "SL Másolása",
        "market_data": "Piaci adatok",
        "trade_data": "Trade adatok",
        "indicators": "Indikátorok",
        "calculations": "Számítások",
        "results": "Eredmények",
        "settings": "Beálitasok",
        "choose":"Kiválasztás",
    },
    "English": {
        "title": "Trade Calculator",
        "balance": "Total Balance:",
        "coin": "Coin:",
        "timeframe": "Timeframe:",
        "length": "Length:",
        "price": "Current Price:",
        "sma": "SMA:",
        "rsi": "RSI:",
        "atr": "ATR:",
        "tp": "Take Profit:",
        "sl": "Stop Loss:",
        "calculate_long": "Calculate LONG",
        "calculate_short": "Calculate SHORT",
        "copy_tp": "Copy TP",
        "copy_sl": "Copy SL",
        "market_data": "Market Data",
        "trade_data": "Trade Data",
        "indicators": "Indicators",
        "calculations": "Calculations",
        "results": "Results",
        "settings": "Settings",
        "choose":"Choose",
    }
}

# Nyelv állapota
current_lang = "English"
  
# Nyelvváltó függvény
def switch_language():
    global current_lang
    current_lang = lang_var.get()
    update_texts()

# GUI elemek szövegének frissítése
def update_texts():
    lang = LANGUAGES[current_lang]
    root.title(lang["title"])
    market_frame.config(text=lang["market_data"])
    trade_frame.config(text=lang["trade_data"])
    indicator_frame.config(text=lang["indicators"])
    result_frame.config(text=lang["calculations"])
    result_frame.config(text=lang["results"])
    button_choose.config(text=lang["choose"])
    #settings_label.confing(text=lang["settings"])
      
  

#Beálitasok ablak 
def open_settings_window():
    global settings_window,Sma_length_var,length_entry_var,lang_var
    if settings_window is None or not settings_window.winfo_exists():  # Ha nincs még nyitva vagy bezárták
# Beállítások ablak létrehozása
     settings_window = tk.Toplevel(root)
     settings_window.title(LANGUAGES[current_lang]["settings"])
     settings_window.geometry("300x300")  # Ablak mérete
     
      # StringVar az Sma length tárolásához
     
     
# Beállítások szöveg
     settings_label = ttk.Label(settings_window, text=LANGUAGES[current_lang]["settings"], font=("Arial", 14, "bold"))
     settings_label.grid(row=0, column=0, columnspan=2, pady=10)

     Sma_length_var = tk.StringVar()
     length_entry_var=tk.StringVar()
     lang_var = tk.StringVar(value="English")
#sma lenght entry
     tk.Label(settings_window, text="Sma length:").grid()
     Sma_length_entry = tk.Entry(settings_window,textvariable=Sma_length_var)
   
     Sma_length_var.set(sma_length)
     Sma_length_entry.grid()
     
#indikator length     
     tk.Label(settings_window, text="Indikator length:").grid()
     length_entry = tk.Entry(settings_window,textvariable=length_entry_var)
     
     length_entry_var.set(length)
     length_entry.grid()

     
     lang_menu = ttk.Combobox(settings_window, textvariable=lang_var, values=["Magyar", "English"], state="readonly")
     lang_menu.grid()
     lang_menu.bind("<<ComboboxSelected>>", lambda e: switch_language())




#gomb
     save_button = tk.Button(settings_window, text="Save", command=save_settings)
     save_button.grid(pady=10)


     
     
def save_settings():
  global sma_length,length  # Ezzel a változóval fogjuk frissíteni az SMA hosszát
  sma_length = int(Sma_length_var.get())  # Frissítjük az SMA hosszát a beállítások szerint
  length=int(length_entry_var.get())
  update_texts()  # Frissítjük a szövegeket a beállítások szerint



def create_entry_field(frame, label_text, default_value, row):
    label =tk.Label(frame, text=label_text)
    label.grid(row=row,column=0, padx=10, pady=5, sticky="W")
    
    entry = tk.Entry(frame)
    entry.insert(0, default_value)
    entry.grid(row=row,column=1,padx=10, pady=5, sticky="EW")
    return entry
  
def plot_chart():
    global df
    macd_var_option = macd_var.get()
    get_data()
    try:
     df = get_data_for_chart()
     
     for widget in chart_frame.winfo_children():
        widget.destroy()
     if macd_var_option is False:   
        fig = Figure(figsize=(14, 5), dpi=100)
        fig.tight_layout(pad=5.0)
        ax1 = fig.add_subplot(211)
        ax2=fig.add_subplot(212)
        ax1.grid(True)
        ax2.grid(True)
     else:
        fig = Figure(figsize=(14, 7), dpi=100)
        fig.tight_layout(pad=5.0)
        ax1 = fig.add_subplot(311)
        ax2=fig.add_subplot(312)
        # Növeli a margókat
        ax3=fig.add_subplot(313)
        ax3.grid(True)  
        ax1.grid(True)
        ax2.grid(True)
     

    
     '''fig, axes = Figure(figsize=(10, 12), dpi=100).subplots(3, 1, sharex=True)
     ax1, ax2, ax3 = axes'''
    
#ax1
     # Plot the close prices and indicators
     ax1.plot(df.index, df['close'], label='Close Price')
     ax1.plot(df.index, df['SMA'], label='SMA')
     
     ax1.plot(df.index, df['Bollinger High'], label='Bollinger High', linestyle='--')
     ax1.plot(df.index, df['Bollinger Low'], label='Bollinger Low', linestyle='--')
     ax1.set_title('Price and SMA')
     ax1.set_xlabel('Date')
     ax1.set_ylabel('Price')
     ax1.legend( loc='upper left')
     

     #ax2
     ax2.plot(df.index, df['K'], label='%K')
     ax2.plot(df.index, df['D'], label='%D')
     ax2.axhline(y=0.8, color='red', linestyle='--', label='Overbought')
     ax2.axhline(y=0.2, color='green', linestyle='--', label='Oversold')
     
     ax2.set_ylabel('Stochastic RSI')
     ax2.legend(loc='upper left')
     

     #ax3
     
     macd_var_option = macd_var.get()
     if macd_var_option is True:
        
        ax3.plot(df.index, df['MACD'], label='MACD')
        ax3.plot(df.index, df['MACD Signal'], label='MACD Signal')
       
        ax3.set_xlabel('Date')
        ax3.set_ylabel('MACD')
        ax3.legend()

    
    
     #plt.tight_layout(pad=2.0)
     # Create a canvas and add the figure to it
     canvas = FigureCanvasTkAgg(fig, master=chart_frame)
     canvas.draw()
     canvas.get_tk_widget().grid(row=0, column=0, padx=10, pady=10, sticky="NSEW")
    
    
    
    
    
    except Exception as e: 
        
         # Hibanyomvonal kibontása
        tb = traceback.extract_tb(e.__traceback__)
        last_call = tb[-1]  # Az utolsó hívás
        line_number = last_call.lineno  # Sor szám
        error_message = f"Hiba a soron {line_number}-nál: {e}"  # Hibaüzenet
        print(error_message)  # Hibák kiíratása (vagy naplózás)




  
  
  

# GUI felépítése
root = tk.Tk()

rows, cols = 3, 4  # Sorok és oszlopok száma
for row in range(rows):
    root.rowconfigure(row, weight=1)
for col in range(cols):
    root.columnconfigure(col, weight=1)


style = ttk.Style()
style.configure("TEntry", justify="left")
style.theme_use("vista")
dark_mode = False

rows, cols = 2, 4  # Sorok és oszlopok száma
for row in range(rows):
    root.rowconfigure(row, weight=1)
for col in range(cols):
    root.columnconfigure(col, weight=1)

#iconok

gear_icon = Image.open("gear.png")

gear_icon_resized = gear_icon.resize((50, 50))
gear_icon_tk = ImageTk.PhotoImage(gear_icon_resized)
  
  
#check box value tp
custom_var_tp = tk.BooleanVar(value=False)
#check box value
custom_var = tk.BooleanVar(value=False)
#check box value sl
custom_var_sl = tk.BooleanVar(value=False)
#check box value sl
settings_window = None 
macd_var = tk.BooleanVar(value=False)
settings_window = None





# Menüsor létrehozása
# 1. Market Data Frame
market_frame = ttk.LabelFrame(root, text="Market Data", padding=10)
market_frame.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
market_frame.rowconfigure(0, weight=1)
market_frame.columnconfigure(0, weight=1)

# 2. Trade Data Frame
trade_frame = ttk.LabelFrame(root, text="Trade Data", padding=10)
trade_frame.grid(row=1, column=2, padx=5, pady=5, sticky="nsew")
trade_frame.rowconfigure(0, weight=1)
trade_frame.columnconfigure(0, weight=1)





# 3. Indicator Frame
indicator_frame = ttk.LabelFrame(root, text="Indicator", padding=10)
indicator_frame.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
indicator_frame.rowconfigure(0, weight=1)
indicator_frame.columnconfigure(0, weight=1)



# 4. Results Frame
result_frame = ttk.LabelFrame(root, text="Results", padding=10)
result_frame.grid(row=1, column=3, padx=5, pady=5, sticky="nsew")
result_frame.rowconfigure(0, weight=1)
result_frame.columnconfigure(0, weight=1)


# Harmadik sor (chart középen)
chart_frame = ttk.LabelFrame(root, text="Chart", padding=10)
chart_frame.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
chart_frame.rowconfigure(0, weight=1)
chart_frame.columnconfigure(0, weight=1)















#Market data frame elemek


# Választó widget létrehozása
option_var = tk.StringVar(value=options[0])  # Alapértelmezett érték
dropdown = tk.OptionMenu(market_frame, option_var, *options)  # Legördülő menü
dropdown.grid(row=0, column=0, padx=10, pady=5, sticky="W")  # Elhelyezés

# Gomb, amely megjeleníti a kiválasztott elemet
button_choose = tk.Button(market_frame,text="choose", command=show_selection)
button_choose.grid(row=0, column=1, padx=10, pady=5, sticky="W")




# Coin beviteli mező
coin_entry=create_entry_field(market_frame, "Coin:", "btc",1)

#price mezo
price_entry=create_entry_field(market_frame, "Price:", "100000",2)

#take profit mezo
tp_custom_entry=create_entry_field(market_frame, "Take profit:", "110000",3)
#take profit masolo
copy_button_tp = ttk.Button(market_frame, text="Tp copy", command=lambda:copy_to_clipboard(tp_custom_entry))
copy_button_tp.grid(row=4, column=1, padx=10, pady=5, sticky="W")

# Checkbox létrehozása tp
checkbox_tp = tk.Checkbutton(market_frame, text="Enable custom take profit", variable=custom_var_tp)
checkbox_tp.grid(row=4, column=0, padx=10, pady=5, sticky="W")
#stop lost mezo
stop_lost_custom_entry=create_entry_field(market_frame, "Stop lost:", "95000",5)
#stop lost masolo
copy_button_sl = ttk.Button(market_frame, text="Sl copy", command=lambda:copy_to_clipboard(stop_lost_custom_entry))
copy_button_sl.grid(row=6, column=1, padx=10, pady=5, sticky="W")
# Checkbox létrehozása sl
checkbox_tp = tk.Checkbutton(market_frame, text="Enable custom stop lost", variable=custom_var_sl)
checkbox_tp.grid(row=6, column=0, padx=10, pady=5, sticky="W")


#indikator frame elemek

#atr mezo
atr_entry=create_entry_field(indicator_frame, "ATR:", "500",0)
#simple moving avarge
sma_entry=create_entry_field(indicator_frame, "SMA:", "101000",1)
#rsi
rsi_entry=create_entry_field(indicator_frame, "RSI:", "50",2)
#stoch rsi
stoch_rsi_entry=create_entry_field(indicator_frame, "Stoch RSI:", "50",3)

#adatok lekeres gomb
get_data_button=tk.Button(indicator_frame, text="Get data", command=get_all_data)
get_data_button.grid(row=4, column=0, padx=10, pady=5, sticky="W")




#trade data frame elemek
#balance mezo
balance_entry = create_entry_field(trade_frame, "Balance:", "100", 0)


#kockázat beálitása
risk_entry=create_entry_field(trade_frame, "Risk percentage:", "2",1)

# Pénznem kiválasztása
tk.Label(trade_frame, text="currency:").grid(row=2, column=0, padx=10, pady=5, sticky="N")


currency_var = tk.StringVar(value='$')
tk.Radiobutton(trade_frame, text="USD ($)", variable=currency_var, value='$').grid(row=3, column=0, padx=10, pady=5, sticky="N")
tk.Radiobutton(trade_frame, text="EUR (€)", variable=currency_var, value='€').grid(row=3, column=1, padx=10, pady=5, sticky="N")
tk.Radiobutton(trade_frame, text="HUF (Ft)", variable=currency_var, value='Ft').grid(row=4, column=0, padx=10, pady=5, sticky="N")
# idosav kivalasztasa
timeframe_label = tk.Label(trade_frame, text="Timeframe:").grid(row=5 ,column=0, padx=10, pady=5, sticky="N")
time_var = tk.StringVar(value=60)
tk.Radiobutton(trade_frame, text="1 (m)", variable=time_var, value=1).grid(row=6, column=0, padx=10, pady=5, sticky="N")
tk.Radiobutton(trade_frame, text="15 (m)", variable=time_var, value=15).grid(row=7, column=0, padx=10, pady=5, sticky="N")
tk.Radiobutton(trade_frame, text="1 (H)", variable=time_var, value=60).grid(row=8, column=0, padx=10, pady=5, sticky="N")
tk.Radiobutton(trade_frame, text="4 (H)", variable=time_var, value=240).grid(row=6, column=1, padx=10, pady=5, sticky="N")
tk.Radiobutton(trade_frame, text="1 (D)", variable=time_var, value='D').grid(row=7, column=1, padx=10, pady=5, sticky="N")

# Checkbox létrehozása 
#checkbox_custom = tk.Checkbutton(root, text="Enable custom price", variable=custom_var)
#checkbox_custom.grid()



#results frame elemek

#beálitasok gomb
settings_button = ttk.Button(result_frame,image=gear_icon_tk, command=open_settings_window)
settings_button.grid(row=1, column=2,padx=5, pady=5,sticky="w")
# Radiobutton változó
trade_var = tk.StringVar(value="LONG")  # Alapértelmezett: "Long"

frame_radio = tk.Frame(root)
frame_radio.grid(pady=10)  # Egy kis távolság a kerettől

# Radiobutton létrehozása
radiobutton_long = tk.Radiobutton(result_frame, text="Long", variable=trade_var, value="LONG")
radiobutton_short = tk.Radiobutton(result_frame, text="Short", variable=trade_var, value="SHORT")

# Checkbox létrehozása sl
macd_var_button = tk.Checkbutton(result_frame, text="Enable Macd indicator", variable=macd_var)
macd_var_button.grid(row=1, column=1, padx=10, pady=5, sticky="W")



# Radiobutton elhelyezése egymás mellett
radiobutton_long.grid(row=1, column=0, padx=10, pady=5, sticky="w")
radiobutton_short.grid(row=2, column=0, padx=10, pady=5, sticky="w")



#számito gomb
calculate_button = tk.Button(result_frame, text="Calculate", command=lambda: calculate_trade(trade_var.get()))
calculate_button.grid(row=3, column=0, padx=10, pady=5, sticky="w")

# Button to plot chart
plot_button = tk.Button(result_frame, text="Plot Chart", command=plot_chart)   
plot_button.grid(row=3, column=1, padx=10, pady=5, sticky="w")



# Eredmény megjelenítése
result_label = tk.Label(root, text="", justify="left")
result_label.grid(row=4, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

# Eredmény megjelenítése (színes szöveg widget)
result_text_widget = tk.Text(result_frame, height=10, width=80,state=tk.DISABLED)
result_text_widget.grid(row=5, column=0, columnspan=4, padx=10, pady=5, sticky="nsew")



#szinek bealitasa
result_text_widget.tag_configure("good", foreground="green")
result_text_widget.tag_configure("neutral", foreground="orange")
result_text_widget.tag_configure("bad", foreground="red")
result_text_widget.tag_configure("info", foreground="blue")












# Indítás
root.mainloop()