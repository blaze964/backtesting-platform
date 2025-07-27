from fetch_yahoo import fetch_historical_data, fetch_fundamental_metrics

# Test parameters
symbol = "TCS"
start_date = "2020-01-01"
end_date = "2023-12-31"

# Test historical data fetch
print("\n📊 Testing Historical Data Fetch:")
historical = fetch_historical_data(symbol, start_date, end_date)
print(historical.head())

# Test fundamental metrics fetch
print("\n📈 Testing Fundamental Metrics Fetch:")
fundamentals = fetch_fundamental_metrics(symbol)
print(fundamentals)
