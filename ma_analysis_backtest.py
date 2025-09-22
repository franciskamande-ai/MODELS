# TASKS:
# 1. Download AAPL data for 2023
# 2. Calculate 20-day and 50-day simple moving averages (SMA)
# 3. Plot Closing Price + both MAs on one chart
# 4. Add visual buy/sell signals (when 20MA crosses above/below 50MA)
# 5. Make it look clean with labels, legend, etc.
# 6. Calulate financial metrics
# 7. Evaluate perfomance and compare with benchmark


import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt
import datetime as dt
import pandas as pd

#So bro am assuming YF will give me the interval as 1D so i won't conver to calculate ma's
ticker = "AAPL"
end = dt.datetime.now()
start = "2023-01-01"

data = yf.download(ticker,start,end,auto_adjust=True)


closing_prices = data['Close']

returns = np.log(closing_prices/closing_prices.shift(1))

twenty_day_ma = closing_prices.rolling(window=20).mean()
fifty_day_ma = closing_prices.rolling(window=50).mean()

buy_signal = (twenty_day_ma > fifty_day_ma) & (twenty_day_ma.shift(1) <= fifty_day_ma).astype(bool)
sell_signal = (fifty_day_ma > twenty_day_ma) & (fifty_day_ma.shift(1) <= twenty_day_ma).astype(bool)

buy_prices = closing_prices[buy_signal]
buy_dates = closing_prices.index

sell_prices = closing_prices[sell_signal]
sell_dates = closing_prices.index


plt.plot(closing_prices,label=f"{ticker} Closing prices")
plt.scatter(buy_dates,buy_prices,marker="^",color="green",s=100,zorder=5,label="Buy signals")
plt.scatter(sell_dates,sell_prices,marker="v",color="red",s=100,zorder=5,label="Sell signals")
plt.plot(twenty_day_ma,label="20 Day MA")
plt.plot(fifty_day_ma,label="50 Day MA")
plt.title(f"AAPL Closing prices since {start} to {end} with 50&20 Day Moving Averages")
plt.legend()
plt.tight_layout()
plt.grid(True)
plt.show()

# PHASE TWO # 

# PHASE 2: STRATEGY BACKTESTING

# --- Portfolio Simulation ---
initial_capital = 10000  # Start with $10,000
portfolio_value = [initial_capital]  # Track portfolio value over time
in_position = False  # Are we currently invested?
cash = initial_capital
shares = 0

# Ensure buy/sell signals are Series (not DataFrame)
buy_signal = buy_signal.squeeze()
sell_signal = sell_signal.squeeze()
closing_prices = closing_prices.squeeze()

# Strategy simulation
for i in range(1, len(closing_prices)):
    current_price = closing_prices.iloc[i]

    # Buy signal
    if bool(buy_signal.iloc[i]) and not in_position:
        shares = cash / current_price  # Buy with all cash
        cash = 0
        in_position = True
    
    # Sell signal
    elif bool(sell_signal.iloc[i]) and in_position:
        cash = shares * current_price  # Sell all shares
        shares = 0
        in_position = False
    
    # Update portfolio value
    if in_position:
        portfolio_value.append(shares * current_price)
    else:
        portfolio_value.append(cash)

# Convert to pandas Series (force float dtype)
portfolio_series = pd.Series(portfolio_value, index=closing_prices.index, dtype="float64")

# --- Buy & Hold Benchmark ---
buy_hold_shares = initial_capital / closing_prices.iloc[0]
buy_hold_value = buy_hold_shares * closing_prices
buy_hold_value = pd.Series(buy_hold_value, index=closing_prices.index, dtype="float64")

# --- Returns ---
strategy_returns = portfolio_series.pct_change().dropna()
strategy_returns = pd.to_numeric(strategy_returns, errors="coerce")

buy_hold_returns = buy_hold_value.pct_change().dropna()
buy_hold_returns = pd.to_numeric(buy_hold_returns, errors="coerce")

# --- Performance metrics ---
final_strategy_value = float(portfolio_series.iloc[-1])
final_buy_hold_value = float(buy_hold_value.iloc[-1])

strategy_total_return = (final_strategy_value - initial_capital) / initial_capital
buy_hold_total_return = (final_buy_hold_value - initial_capital) / initial_capital

# Annualized Sharpe ratio (risk-free rate = 0)
if strategy_returns.std() == 0 or np.isnan(strategy_returns.std()):
    strategy_sharpe = np.nan
else:
    strategy_sharpe = np.sqrt(252) * (strategy_returns.mean() / strategy_returns.std())

if buy_hold_returns.std() == 0 or np.isnan(buy_hold_returns.std()):
    buy_hold_sharpe = np.nan
else:
    buy_hold_sharpe = np.sqrt(252) * (buy_hold_returns.mean() / buy_hold_returns.std())

# --- Results ---
print("=" * 50)
print("BACKTEST RESULTS: 20/50 MA Crossover Strategy")
print("=" * 50)
print(f"Initial Capital: ${initial_capital:,.2f}")
print(f"Final Strategy Value: ${final_strategy_value:,.2f}")
print(f"Final Buy & Hold Value: ${final_buy_hold_value:,.2f}")
print(f"Strategy Total Return: {strategy_total_return:.2%}")
print(f"Buy & Hold Total Return: {buy_hold_total_return:.2%}")
print(f"Strategy Sharpe Ratio: {strategy_sharpe:.2f}")
print(f"Buy & Hold Sharpe Ratio: {buy_hold_sharpe:.2f}")
print(f"Number of Trades: {len(buy_signal[buy_signal]) + len(sell_signal[sell_signal])}")
print("=" * 50)

# --- Plot performance comparison ---
plt.figure(figsize=(12, 8))

# Portfolio value comparison
plt.subplot(2, 1, 1)
plt.plot(portfolio_series, label='MA Crossover Strategy', linewidth=2)
plt.plot(buy_hold_value, label='Buy & Hold', linewidth=2, alpha=0.7)
plt.title('Portfolio Value Comparison: $10,000 Initial Investment')
plt.ylabel('Portfolio Value ($)')
plt.legend()
plt.grid(True, alpha=0.3)

# Drawdown comparison
plt.subplot(2, 1, 2)
strategy_drawdown = (portfolio_series - portfolio_series.cummax()) / portfolio_series.cummax()
buy_hold_drawdown = (buy_hold_value - buy_hold_value.cummax()) / buy_hold_value.cummax()
plt.plot(strategy_drawdown, label='Strategy Drawdown', linewidth=1)
plt.plot(buy_hold_drawdown, label='Buy & Hold Drawdown', linewidth=1)
plt.title('Maximum Drawdown Comparison')
plt.ylabel('Drawdown (%)')
plt.xlabel('Date')
plt.legend()
plt.grid(True, alpha=0.3)

plt.tight_layout()
plt.show()

# --- Trade Log ---
print("\nTRADE LOG:")
print("Date         | Action | Price     | Portfolio Value")
print("-" * 50)
for i in range(1, len(closing_prices)):
    if bool(buy_signal.iloc[i]):
        print(f"{closing_prices.index[i].date()} | BUY    | ${closing_prices.iloc[i]:.2f} | ${portfolio_series.iloc[i]:,.2f}")
    elif bool(sell_signal.iloc[i]):
        print(f"{closing_prices.index[i].date()} | SELL   | ${closing_prices.iloc[i]:.2f} | ${portfolio_series.iloc[i]:,.2f}")

```
