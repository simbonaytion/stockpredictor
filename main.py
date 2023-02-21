import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from pycoingecko import CoinGeckoAPI
from matplotlib.widgets import RadioButtons

# ------------------------------------------------------------------------------------------------------------------------------------------------------------

def get_crypto_data(crypto_ids, start_date, end_date):
    cg = CoinGeckoAPI()
    # Retrieve the price data for each crypto in the array from the CoinGecko API
    crypto_data = {}
    for crypto_id in crypto_ids:
        data = cg.get_coin_market_chart_range_by_id(id=crypto_id, vs_currency='usd', from_timestamp=start_date.timestamp(), to_timestamp=end_date.timestamp())
        prices = [ts[1] for ts in data['prices']]
        prices_normalized = [100 * price / prices[0] - 100 for price in prices]
        dates = [datetime.fromtimestamp(ts[0]/1000) for ts in data['prices']]
        df = pd.DataFrame(prices_normalized, index=dates, columns=[f'{crypto_id.title()} Price'])
        df = df.resample('D').ffill()
        crypto_data[crypto_id] = df

    # Combine the data frames for each crypto
    df = pd.concat(crypto_data.values(), axis=1)
    return df, crypto_data

# ------------------------------------------------------------------------------------------------------------------------------------------------------------

def update_plot(label):
    global start_date, end_date, df, crypto_data, fig

    time_delta = {'1 Day':1, '1 Week':7, '1 Month':30, '1 Year':365}
    start_date = end_date - timedelta(days=time_delta[label])

    df, crypto_data = get_crypto_data(crypto_ids, start_date, end_date)

    fig, ax = plt.subplots()
    df.plot(ax=ax, title='Crypto Prices', xlabel='Date', ylabel='Percentage Increase/Decrease', legend=True)

    for widget in fig.get_children():
        if isinstance(widget, RadioButtons):
            widget.remove()
    
    ax_time = plt.axes([0.05, 0.05, 0.2, 0.2], facecolor='lightgray')
    time_options = ('1 Day', '1 Week', '1 Month', '1 Year')
    time_radios = RadioButtons(ax_time, time_options)
    time_radios.on_clicked(update_plot)

    plt.show()

# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# Define the start and end dates
end_date = datetime.today()
start_date = end_date - timedelta(days=365)

# Define an array of crypto ids
crypto_ids = ['solana', 'bitcoin']

# Get the crypto data for the initial time frame
df, crypto_data = get_crypto_data(crypto_ids, start_date, end_date)

# Plot the combined data
fig, ax = plt.subplots()
df.plot(ax=ax, title='Crypto Prices', legend=True)
plt.xlabel('Date')
plt.ylabel('Percentage Increase/Decrease')

# Add the time frame selection widget
ax_time = plt.axes([0.05, 0.05, 0.2, 0.2], facecolor='lightgray')
time_options = ('1 Day', '1 Week', '1 Month', '1 Year')
time_radios = RadioButtons(ax_time, time_options)

# Connect the update function to the widget
time_radios.on_clicked(update_plot)

plt.show()
