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

# Beállítjuk a kontextust, hogy hány tizedesjegyig számoljon
getcontext().prec = 10

# Alapértelmezett értékek
curency = '$'
risk_percent = 2
price=1000
data = []
sma_length=200
length=14
def get_data():
 global data
 try:
    session = HTTP(testnet=False )
    symbol = coin_entry.get().upper()
    time=time_var.get()
    list=(session.get_mark_price_kline(
    category="linear",
    symbol=symbol+"USDT",
    interval=time,))

    data=(list["result"]["list"])
    return data
 except Exception as e:
   messagebox.showerror("Hiba", f" Árfolyam lekérése sikertelenn: {e}")


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
        window = data[i:i + period]  # Az N hosszú részlet
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

"""def calculate_stoch_rsi(rsi_values, period=14):
    
    min_rsi = min(rsi_values[-period:])
    max_rsi = max(rsi_values[-period:])
    if max_rsi - min_rsi == 0:
        return 0
    stoch_rsi = (rsi_values[-1] - min_rsi) / (max_rsi - min_rsi)
    return stoch_rsi""" * 100  # 0-100 skála
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
            root.after(0, get_rsi)  # Safely update RSI
            root.after(0,get_stoch_rsi)
            root.after(0, get_atr)  # Safely update ATR
            root.after(0, get_price)  # Safely update Price
            root.after(0, get_sma,sma_length)  # Safely update SMA
            
        except Exception as e:
            messagebox.showerror("Hiba", f"Hiba történt: {e}")
    threading.Thread(target=worker).start()


# Számítások függvényei
def calculate_trade_details_long(total_balance, current_price, atr, take_profit_custom, risk_percent, curency,custom2):
    
    
    
    
    
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

def calculate_trade_details_short(total_balance, current_price, atr, take_profit_custom, risk_percent, curency,custom2):
    
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
        curency = currency_var.get()
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
                total_balance, current_price, atr, take_profit_custom, risk_percent, curency,custom2)
           
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
                total_balance, current_price, atr, take_profit_custom, risk_percent, curency,custom2)
            
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
        Stop loss helye: {stop_loss}{curency}
        Ideális Take profit 3X hez : {take_profit}{curency}
        Lehetséges nyereség: {profit_potential}%
        Lehetséges veszteség: {loss_potential}%
        Trade mérete: {trade_size}{curency}
        A megadott take profit hellyel a reward-risk ratio = {ratio}
       
        """
        result_text_widget.config(state=tk.NORMAL)
        result_text_widget.delete("1.0", tk.END)
        result_text_widget.insert(tk.END, f"Stop loss helye: {stop_loss}{curency}\n", "info")
        result_text_widget.insert(tk.END, f"Ideális Take profit 2X  hez: {take_profit}{curency}\n", "info")
        result_text_widget.insert(tk.END, f"Lehetséges nyereség: +{profit_potential}%\n", "info")  
        result_text_widget.insert(tk.END, f"Lehetséges veszteség: {max_loss}{curency}\n","bad")
        
        result_text_widget.insert(tk.END, f"Trade mérete: {trade_size}{curency}\n", "info")
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
def align_children_left(parent, **pack_options):
    
    default_options = {"anchor": "w", "pady": 5}  # Alapértelmezett opciók
    default_options.update(pack_options)  # Egyedi opciók hozzáadása
    for child in parent.winfo_children():
        child.pack(**default_options)

# A Take profit értékének másolása a vágólapra
def copy_to_clipboard_tp():
    pyperclip.copy(tp_custom_entry.get())
# A Take profit értékének másolása a vágólapra
def copy_to_clipboard_sl():
    pyperclip.copy(stop_lost_custom_entry.get())





  
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
        "settings": "Beálitasok"
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
        "settings": "Settings"
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
    piaci_adatok_frame.config(text=lang["market_data"])
    trade_adatok_frame.config(text=lang["trade_data"])
    indikator_frame.config(text=lang["indicators"])
    szamitas_frame.config(text=lang["calculations"])
    eredmenyek_frame.config(text=lang["results"])
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
     settings_label.pack(pady=10)

     Sma_length_var = tk.StringVar()
     length_entry_var=tk.StringVar()
     lang_var = tk.StringVar(value="English")
#sma lenght entry
     tk.Label(settings_window, text="Sma length:").pack()
     Sma_length_entry = tk.Entry(settings_window,textvariable=Sma_length_var)
   
     Sma_length_var.set(sma_length)
     Sma_length_entry.pack()
     
#indikator length     
     tk.Label(settings_window, text="Indikator length:").pack()
     length_entry = tk.Entry(settings_window,textvariable=length_entry_var)
     
     length_entry_var.set(length)
     length_entry.pack()

     
     lang_menu = ttk.Combobox(settings_window, textvariable=lang_var, values=["Magyar", "English"], state="readonly")
     lang_menu.pack(pady=5)
     lang_menu.bind("<<ComboboxSelected>>", lambda e: switch_language())




#gomb
     save_button = tk.Button(settings_window, text="Save", command=save_settings)
     save_button.pack(pady=10)


     
     
def save_settings():
  global sma_length,length  # Ezzel a változóval fogjuk frissíteni az SMA hosszát
  sma_length = int(Sma_length_var.get())  # Frissítjük az SMA hosszát a beállítások szerint
  length=int(length_entry_var.get())
    
  
  
  
  
  
  
  
  
  
  

# GUI felépítése
root = tk.Tk()
root.title(LANGUAGES[current_lang]["title"])


style = ttk.Style()
style.configure("TEntry", justify="left")
style.theme_use("vista")
dark_mode = False
#iconok
gear_icon = Image.open("gear.png")
gear_icon_resized = gear_icon.resize((50, 50))
gear_icon_tk = ImageTk.PhotoImage(gear_icon_resized)












# Fő Frame-ek létrehozása

piaci_adatok_frame = ttk.LabelFrame(root, text=LANGUAGES[current_lang]["market_data"], padding=10)
piaci_adatok_frame.pack(side="left",fill="both", expand=True, padx=10, pady=5)

trade_adatok_frame = ttk.LabelFrame(root,text=LANGUAGES[current_lang]["trade_data"], padding=10)
trade_adatok_frame.pack(side="right",fill="both", expand=True, padx=10, pady=5)


indikator_frame = ttk.LabelFrame(root,text=LANGUAGES[current_lang]["indicators"], padding=10)
indikator_frame.pack(fill="both", expand=True, padx=10, pady=5)


szamitas_frame = ttk.LabelFrame(root,text=LANGUAGES[current_lang]["calculations"], padding=10)
szamitas_frame.pack(fill="both", expand=True, padx=10, pady=5)


eredmenyek_frame= ttk.LabelFrame(root, text=LANGUAGES[current_lang]["results"], padding=10)
eredmenyek_frame.pack(fill="both", expand=True, padx=10, pady=5)


frame = tk.Frame(root)
frame.pack(expand=True)
#check box value tp
custom_var_tp = tk.BooleanVar(value=False)
#check box value
custom_var = tk.BooleanVar(value=False)
#check box value sl
custom_var_sl = tk.BooleanVar(value=False)

settings_window = None 



# Beviteli mezők és címkék
tk.Label(trade_adatok_frame, text="Balance").pack()
balance_entry = tk.Entry(trade_adatok_frame)
balance_entry.insert(0,"100")# Alapértelmezett érték
balance_entry.pack()

tk.Label(piaci_adatok_frame, text="coin").pack()
coin_entry = tk.Entry(piaci_adatok_frame)
coin_entry.insert(0, "btc")  # Alapértelmezett érték
coin_entry.pack()

# Választó widget létrehozása
option_var = tk.StringVar(value=options[0])  # Alapértelmezett érték
dropdown = tk.OptionMenu(piaci_adatok_frame, option_var, *options)  # Legördülő menü
dropdown.pack()

# Gomb, amely megjeleníti a kiválasztott elemet
button = tk.Button(piaci_adatok_frame, text="Kiválasztás", command=show_selection)
button.pack()

tk.Label(piaci_adatok_frame, text="price").pack()
price_entry = tk.Entry(piaci_adatok_frame)
price_entry.insert(0,"100000") # Alapértelmezett érték
price_entry.pack()






#atr mezo
tk.Label(indikator_frame, text="ATR:").pack()
atr_entry = tk.Entry(indikator_frame)
atr_entry.insert(0,"500") # Alapértelmezett érték
atr_entry.pack()

#simple moving avarge
tk.Label(indikator_frame, text="SMA").pack()
sma_entry = tk.Entry(indikator_frame)
sma_entry.insert(0,"101000") # Alapértelmezett érték
sma_entry.pack()


#take profit mezo
tk.Label(piaci_adatok_frame, text="Take profit location:").pack()
tp_custom_entry = tk.Entry(piaci_adatok_frame,)
tp_custom_entry.insert(0,"110000")  # Alapértelmezett érték
tp_custom_entry.pack()
#take profit masolo
copy_button = ttk.Button(piaci_adatok_frame, text="Tp copy", command=copy_to_clipboard_tp)
copy_button.pack(pady=10)

# Checkbox létrehozása tp
checkbox_tp = tk.Checkbutton(piaci_adatok_frame, text="Enable custom take profit", variable=custom_var_tp)
checkbox_tp.pack()
#stop lost mezo
tk.Label(piaci_adatok_frame, text="Stop lost location:").pack()
stop_lost_custom_entry = tk.Entry(piaci_adatok_frame,)
stop_lost_custom_entry.insert(0,"95000")  # Alapértelmezett érték
stop_lost_custom_entry.pack()
#stop lost masolo
copy_button = ttk.Button(piaci_adatok_frame, text="Sl copy", command=copy_to_clipboard_sl())
copy_button.pack(pady=10)
# Checkbox létrehozása sl
checkbox_tp = tk.Checkbutton(piaci_adatok_frame, text="Enable custom stop lost", variable=custom_var_sl)
checkbox_tp.pack()

#kockázat beálitása
tk.Label(trade_adatok_frame, text="Risk percentage (%):").pack()
risk_entry = tk.Entry(trade_adatok_frame)
risk_entry.insert(0, "2")  # Alapértelmezett érték
risk_entry.pack()
#rsi
tk.Label(indikator_frame, text="RSI :").pack()
rsi_entry = tk.Entry(indikator_frame)
rsi_entry.insert(0, "50")  # Alapértelmezett érték
rsi_entry.pack()

#stoch rsi

tk.Label(indikator_frame, text="Stoch RSI :").pack()
stoch_rsi_entry = tk.Entry(indikator_frame)
stoch_rsi_entry.insert(0, "50")  # Alapértelmezett érték
stoch_rsi_entry.pack()






# Pénznem kiválasztása
tk.Label(trade_adatok_frame, text="Curency:").pack()


currency_var = tk.StringVar(value='$')
tk.Radiobutton(trade_adatok_frame, text="USD ($)", variable=currency_var, value='$').pack()
tk.Radiobutton(trade_adatok_frame, text="EUR (€)", variable=currency_var, value='€').pack()
tk.Radiobutton(trade_adatok_frame, text="HUF (Ft)", variable=currency_var, value='Ft').pack()
# idosav kivalasztasa
timeframe_label = tk.Label(trade_adatok_frame, text="timeframe").pack()
time_var = tk.StringVar(value=60)
tk.Radiobutton(trade_adatok_frame, text="1 (m)", variable=time_var, value=1).pack()
tk.Radiobutton(trade_adatok_frame, text="15 (m)", variable=time_var, value=15).pack()
tk.Radiobutton(trade_adatok_frame, text="1 (H)", variable=time_var, value=60).pack()
tk.Radiobutton(trade_adatok_frame, text="4 (H)", variable=time_var, value=240).pack()
tk.Radiobutton(trade_adatok_frame, text="1 (D)", variable=time_var, value='D').pack()
#adatok lekeres gomb
get_data_button=tk.Button(indikator_frame, text="Get data", command=get_all_data)
get_data_button.pack()

# Checkbox létrehozása 
#checkbox_custom = tk.Checkbutton(root, text="Enable custom price", variable=custom_var)
#checkbox_custom.pack()





# Radiobutton változó
trade_var = tk.StringVar(value="LONG")  # Alapértelmezett: "Long"

frame_radio = tk.Frame(root)
frame_radio.pack(pady=10)  # Egy kis távolság a kerettől

# Radiobutton létrehozása
radiobutton_long = tk.Radiobutton(szamitas_frame, text="Long", variable=trade_var, value="LONG")
radiobutton_short = tk.Radiobutton(szamitas_frame, text="Short", variable=trade_var, value="SHORT")

# Radiobutton elhelyezése egymás mellett
radiobutton_long.pack(side="left")
radiobutton_short.pack(side="left")



#számito gomb
calculate_button = tk.Button(szamitas_frame, text="Calculate", command=lambda: calculate_trade(trade_var.get()))
calculate_button.pack(side="bottom")



# Eredmény megjelenítése
result_label = tk.Label(root, text="", justify="left")
result_label.pack()

# Eredmény megjelenítése (színes szöveg widget)
result_text_widget = tk.Text(eredmenyek_frame, height=10, width=50,state=tk.DISABLED)
result_text_widget.pack()

#beálitasok gomb
settings_button = ttk.Button(piaci_adatok_frame,image=gear_icon_tk, command=open_settings_window)
settings_button.pack(pady=20)

#szinek bealitasa
result_text_widget.tag_configure("good", foreground="green")
result_text_widget.tag_configure("neutral", foreground="orange")
result_text_widget.tag_configure("bad", foreground="red")
result_text_widget.tag_configure("info", foreground="blue")

# Minden widgetet balra igazítunk a frame-ben
align_children_left(trade_adatok_frame)
align_children_left(indikator_frame)
align_children_left(szamitas_frame)
align_children_left(piaci_adatok_frame)
# Indítás
root.mainloop()
