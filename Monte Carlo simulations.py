import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import yfinance as yf
import datetime as dt

ticker = "EURUSD=X" 
end = dt.datetime.now()
start = end - dt.timedelta(days=365*5)  # 5 years of data

data = yf.download(ticker, start, end)
close_price = data['Close'].dropna()

# Calculate daily log returns
log_returns = np.log(close_price / close_price.shift(1)).dropna()

# Annualize the parameters (252 trading days)
mu_daily = log_returns.mean()
sigma_daily = log_returns.std()

mu_annual = mu_daily * 252
sigma_annual = sigma_daily * np.sqrt(252)

mu_annual = mu_annual.iloc[-1]
sigma_annual = sigma_annual.iloc[-1]

n_simulations = 10000

# Extract scalar values
SO = close_price.iloc[-1]  # This is fine as a Series for initialization
SO_value = SO.item()  # Scalar value for comparisons

T = 1  # 1 year
N = 252  # trading days
dt_val = T / N

time = np.linspace(0, T, N+1)
simulations = np.zeros((N+1, n_simulations))

# CRITICAL: Initialize all simulations with the starting price
simulations[0] = SO_value

for i in range(1, N+1):
    Z = np.random.normal(0, 1, n_simulations)
    # Use the previous day's prices for the simulation
    simulations[i] = simulations[i-1] * np.exp(
        (mu_annual - 0.5 * sigma_annual**2) * dt_val + 
        sigma_annual * np.sqrt(dt_val) * Z
    )

final_prices = simulations[-1]

VaR_95 = np.percentile(final_prices, 5)
prob_loss = np.mean(final_prices < SO_value)
prob_profit = np.mean(final_prices > SO_value)
prob_up = np.mean(final_prices > SO_value * 1.05)

print("== Monte Carlo Simulation Results ==")
print(f"Initial Price: {SO_value:.4f}")
print(f"Expected Price after 1 year: {np.mean(final_prices):.4f}")
print(f"VaR 95: {VaR_95:.4f}")
print(f"Probability of Loss: {prob_loss:.2%}")
print(f"Probability of Profit: {prob_profit:.2%}")
print(f"Probability of 5% Gain: {prob_up:.2%}")
print(f"Annualized Drift (mu): {mu_annual:.4f}")
print(f"Annualized Volatility (sigma): {sigma_annual:.4f}")
print("="*50)

plt.figure(figsize=(12, 6))
plt.plot(time, simulations, alpha=0.8, linewidth=0.5)
plt.title('Monte Carlo Simulations of EUR/USD Price (1 Year Forecast)')
plt.xlabel('Time (Years)')
plt.ylabel('Price')
plt.axhline(SO_value, color='red', linestyle='--', label=f'Starting Price: {SO_value:.4f}')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()

# Additional diagnostic plot
plt.figure(figsize=(10, 6))
plt.hist(final_prices, bins=50, alpha=0.7, edgecolor='black')
plt.axvline(SO_value, color='red', linestyle='--', label='Starting Price')
plt.axvline(np.mean(final_prices), color='green', linestyle='--', label='Expected Price')
plt.title('Distribution of Simulated Final Prices')
plt.xlabel('Price')
plt.ylabel('Frequency')
plt.legend()
plt.grid(True, alpha=0.3)
plt.show()