from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pandas as pd
import numpy as np
from fetch_yahoo import fetch_historical_data, fetch_fundamental_metrics
from dateutil.relativedelta import relativedelta


app = FastAPI()

origions= [
    "http://localhost:3000"
]

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BacktestParams(BaseModel):
    startDate: str
    endDate: str
    frequency: str
    portfolioSize: int
    capital: float
    marketCapMin: float = 0
    marketCapMax: float = 1e15
    roce: float = 0
    pat: bool = False
    rankingLogic: str = ""
    sizingMethod: str

# stock_list = ["TCS", "INFY", "RELIANCE", "HDFCBANK", "ITC", "WIPRO", "LT", "SBIN", "AXISBANK", "HINDUNILVR"]
stock_list = [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", "HINDUNILVR", "SBIN",
    "BHARTIARTL", "BAJFINANCE", "KOTAKBANK", "ITC", "LT", "ASIANPAINT",
    "HCLTECH", "MARUTI", "AXISBANK", "SUNPHARMA", "NTPC", "ULTRACEMCO",
    "TITAN", "NESTLEIND", "TATASTEEL", "POWERGRID", "JSWSTEEL", "TECHM",
    "ADANIENT", "ADANIPORTS", "CIPLA", "BAJAJFINSV", "COALINDIA", "ONGC",
    "HDFCLIFE", "GRASIM", "DRREDDY", "DIVISLAB", "BRITANNIA", "BPCL",
    "EICHERMOT", "HINDALCO", "UPL", "SBILIFE", "INDUSINDBK", "HEROMOTOCO",
    "SHREECEM", "TATAMOTORS", "WIPRO", "BAJAJ-AUTO", "M&M", "APOLLOHOSP",
    "ICICIPRULI"
]


def get_fundamentals(symbol):
    data = fetch_fundamental_metrics(symbol)
    if "error" in data:
        return None
    return {
        "symbol": symbol,
        "marketCap": data.get("marketCap", 0),
        # "ROCE": data.get("returnOnEquity", 0) * 100 if data.get("returnOnEquity") else 0,
        "ROCE": data.get("returnOnEquity", 0) * 100 if data.get("returnOnEquity") is not None else 0,
        "PAT": 1  # Placeholder for PAT
    }

def get_historical_data(symbol, start, end):
    df = fetch_historical_data(symbol, start, end)
    if df.empty:
        return pd.DataFrame()
    return df.reset_index()[["Date", "Close"]]

@app.post("/backtest")
async def run_backtest(params: BacktestParams):
    try:
        print("Received params:", params)

        def generate_rebalance_dates(start_date, end_date, frequency):
            dates = []
            current = pd.to_datetime(start_date)
            end = pd.to_datetime(end_date)
            while current < end:
                dates.append(current)
                if frequency == "Monthly":
                    current += relativedelta(months=1)
                elif frequency == "Quarterly":
                    current += relativedelta(months=3)
                elif frequency == "Yearly":
                    current += relativedelta(years=1)
                else:
                    break
            dates.append(end)
            return dates

        rebalance_dates = generate_rebalance_dates(params.startDate, params.endDate, params.frequency)
        portfolio_history = []
        capital = params.capital

        for i in range(len(rebalance_dates) - 1):
            rebalance_start = rebalance_dates[i]
            rebalance_end = rebalance_dates[i + 1]

            selected_stocks = []
            fundamentals = []

            for symbol in stock_list:
                f = get_fundamentals(symbol)
                # print(f"{symbol} fundamentals: {f}")  # ✅ 

                if f is None:
                    continue

                # Apply filters

                mc = f.get("marketCap", 0)
                roce = f.get("ROCE", 0)
                pat = f.get("PAT", 0)
                
                print(f"{symbol} ➤ marketCap: {mc}, ROCE: {roce}, PAT: {pat}")
                print(f"Checking if {mc} ∈ [{params.marketCapMin}, {params.marketCapMax}] and ROCE ≥ {params.roce}")

                if (mc >= params.marketCapMin 
                    and mc <= params.marketCapMax 
                    and roce >= params.roce):
                        
                    if not params.pat or pat > 0:
                    # if roce >= 0:    
                        fundamentals.append(f)
                        print(f"✅ Added {symbol}")
                    else:
                        print(f"❌ Rejected {symbol} due to PAT filter")

                else:
                        print(f"❌ Rejected {symbol} due to marketCap/ROCE filter")

                        
            ranked = sorted(fundamentals, key=lambda x: x["ROCE"], reverse=True)
            selected_stocks = ranked[:params.portfolioSize]

            if not selected_stocks:
                print(f"Total filtered stocks: {len(fundamentals)}")
                return {"error": "No stocks matched the filter criteria."}

            if params.sizingMethod == "Equal Weight":
                weights = [1 / len(selected_stocks)] * len(selected_stocks)
            elif params.sizingMethod == "Market Cap Weighted":
                total_mc = sum(s["marketCap"] for s in selected_stocks)
                weights = [s["marketCap"] / total_mc for s in selected_stocks]
            elif params.sizingMethod == "ROCE Weighted":
                total_roce = sum(s["ROCE"] for s in selected_stocks)
                weights = [s["ROCE"] / total_roce for s in selected_stocks]
            else:
                weights = [1 / len(selected_stocks)] * len(selected_stocks)

            logs = []
            for i, symbol_data in enumerate(selected_stocks):
                symbol = symbol_data["symbol"]
                hist = get_historical_data(symbol, params.startDate, params.endDate)
                if hist.empty:
                    continue
                # hist["Weight"] = weights[i]
                hist["Investment"] = params.capital * weights[i]

                if "Weight" in hist.columns:
                    hist["Weight"] = hist["Weight"].fillna(method="ffill")
                else:
                    hist["Weight"] = weights[i]  # fallback

                if "Returns" in hist.columns:
                    hist["Returns"] = hist["Returns"].fillna(method="ffill")
                else:
                    hist["Returns"] = 0  # fallback

                # Step 1: Get the price on the buy date (first row)
                buy_price = hist["Close"].iloc[0]

                # Step 2: Calculate shares bought on that date
                shares = (params.capital * weights[i]) / buy_price

                # Step 3: Add a new column with fixed shares
                hist["Shares"] = shares

                # Step 4: Calculate value daily using changing close prices
                hist["Value"] = hist["Shares"] * hist["Close"]

                # hist["Shares"] = hist["Investment"] / hist["Close"]
                # hist["Value"] = hist["Shares"] * hist["Close"]
                hist["Symbol"] = symbol
                logs.append(hist)

            if not logs:
                return {"error": "No historical data available for selected stocks."}

            combined = pd.concat(logs)
            portfolio = combined.groupby("Date")["Value"].sum().reset_index()
            portfolio["Returns"] = portfolio["Value"].pct_change()
            portfolio["Cumulative"] = (1 + portfolio["Returns"]).cumprod()
            capital = portfolio["Value"].iloc[-1]
            portfolio_history.append(portfolio)

        if not portfolio_history:
            return {"error": "No valid rebalance periods with data."}
        
        full_portfolio = pd.concat(portfolio_history)
        full_portfolio = full_portfolio.drop_duplicates(subset="Date").sort_values("Date")
        full_portfolio["Returns"] = full_portfolio["Value"].pct_change()
        full_portfolio["Cumulative"] = (1 + full_portfolio["Returns"]).cumprod()

        start_val = full_portfolio["Value"].iloc[0]
        end_val = full_portfolio["Value"].iloc[-1]
        # years = (full_portfolio["Date"].iloc[-1] - full_portfolio["Date"].iloc[0]).days / 365
        start_date = pd.to_datetime(full_portfolio["Date"].iloc[0])
        end_date = pd.to_datetime(full_portfolio["Date"].iloc[-1])
        years = (end_date - start_date).days / 365

        cagr = ((end_val / start_val) ** (1 / years)) - 1

        # start_val = portfolio["Value"].iloc[0]
        # end_val = portfolio["Value"].iloc[-1]
        # years = (portfolio["Date"].iloc[-1] - portfolio["Date"].iloc[0]).days / 365
        # cagr = ((end_val / start_val) ** (1 / years)) - 1
        
        # sharpe = portfolio["Returns"].mean() / portfolio["Returns"].std() * np.sqrt(12)
        returns = portfolio["Returns"]
        sharpe = (
            (returns.mean() / returns.std() * np.sqrt(12))
            if returns.std() != 0 and not np.isnan(returns.std())
            else 0 )

        drawdown = portfolio["Cumulative"] / portfolio["Cumulative"].cummax() - 1
        max_dd = drawdown.min()

        metrics = {
            "CAGR": round(cagr * 100, 2),
            "Sharpe Ratio": round(sharpe, 2),
            "Max Drawdown": round(max_dd * 100, 2)
        }

        # winners = sorted(selected_stocks, key=lambda x: x["ROCE"], reverse=True)[:3]
        # losers = sorted(selected_stocks, key=lambda x: x["ROCE"])[:3]
        # Calculate actual returns from historical data
        returns_by_symbol = {}
        for log in logs:
            symbol = log["Symbol"].iloc[0]
            start_price = log["Close"].iloc[0]
            end_price = log["Close"].iloc[-1]
            total_return = (end_price - start_price) / start_price
            returns_by_symbol[symbol] = total_return

        # Sort by actual return
        sorted_returns = sorted(returns_by_symbol.items(), key=lambda x: x[1], reverse=True)
        winners = [{"symbol": sym, "return": round(ret * 100, 2)} for sym, ret in sorted_returns[:3]]
        losers = [{"symbol": sym, "return": round(ret * 100, 2)} for sym, ret in sorted_returns[-3:]]

        # Make dates timezone unaware for Excel
        combined["Date"] = pd.to_datetime(combined["Date"]).dt.tz_localize(None)
        portfolio["Date"] = pd.to_datetime(portfolio["Date"]).dt.tz_localize(None)

        combined.to_csv("portfolio_logs.csv", index=False)
        combined.to_excel("portfolio_logs.xlsx", index=False)

        return {
            "metrics": metrics,
            "winners": winners,
            "losers": losers,
            "logs": combined.tail(5).to_dict(orient="records"),
            "equityCurve": portfolio[["Date", "Cumulative"]].dropna().to_dict(orient="records"),
            "drawdown": pd.DataFrame({"Date": portfolio["Date"],"Drawdown": drawdown.fillna(0)}).to_dict(orient="records"),
            "drawdown": pd.DataFrame({"Date": portfolio["Date"],"Drawdown": drawdown.fillna(0),"Returns": portfolio["Returns"].fillna(0)}).to_dict(orient="records")
        }
    except Exception as e:
        print("❌ Error in /backtest:", str(e))
        return {"error": str(e)}

@app.get("/download/csv")
def download_csv():
    return FileResponse("portfolio_logs.csv", media_type="text/csv", filename="portfolio_logs.csv")

@app.get("/download/excel")
def download_excel():
    return FileResponse("portfolio_logs.xlsx", media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", filename="portfolio_logs.xlsx")
