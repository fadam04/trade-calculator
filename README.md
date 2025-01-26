# trade-calculator
My first programing project ever
The **Trade Calculator** is a Python-based graphical user interface (GUI) application designed to help traders analyze market data and calculate trading strategies. The program calculates technical indicators (e.g., RSI, SMA, ATR) and displays market data on charts.
The program get data from the bybit api.
You can add custom coin but use ticker name for example:btc,eth,sol



## **Features**

- **Market Data Retrieval**: The program retrieves real-time market data using the Bybit API.
- **Technical Indicators**:
  - RSI (Relative Strength Index)
  - SMA (Simple Moving Average)
  - ATR (Average True Range)
  - StochRSI (Stochastic RSI)
  - MACD (Moving Average Convergence Divergence)
- **Trade Calculations**:
  - Calculate Stop Loss and Take Profit levels.
  -The Sl calculated by 3*atr the take profits are calculated by past high and lows.
  - Display Risk-Reward ratio.
  - Calculate trade size.
- **Graphical Visualization**:
  - Display price charts and technical indicators.
- **Language Support**:
  - The program is available in both English and Hungarian.

## **Installation**

### **Prerequisites**
- Python 3.7 or later.
- Install the required libraries:

  ```bash
  pip install pybit pandas numpy ta matplotlib pillow pyperclip
  
## Running the Program
You can run with just the python file or using the exe
