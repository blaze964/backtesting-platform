from datetime import datetime
import pandas as pd
import yfinance as yf
from sqlalchemy.orm import Session
from models import StockPrice, Fundamental
from database import SessionLocal
import numpy as np
from sqlalchemy import func


def fetch_historical_data(ticker_symbol, start_date, end_date):
    session: Session = SessionLocal()
    try:
        # Check if data already exists in DB
        existing = session.query(StockPrice).filter(
            StockPrice.symbol == ticker_symbol,
            StockPrice.date >= start_date,
            StockPrice.date <= end_date
        ).all()

        if existing:
            print(f"✅ Loaded historical data for {ticker_symbol} from DB")
            df = pd.DataFrame([{
                "Date": row.date,
                "Open": row.open,
                "High": row.high,
                "Low": row.low,
                "Close": row.close,
                "Volume": row.volume
            } for row in existing])
            return df.set_index("Date")

        # Fetch from yfinance
        ticker = yf.Ticker(f"{ticker_symbol}.NS")
        data = ticker.history(start=start_date, end=end_date)
        if data.empty:
            print(f"⚠️ No historical data found for {ticker_symbol}")
            return pd.DataFrame()

        # Store in DB
        for date, row in data.iterrows():
            record = StockPrice(
                symbol=ticker_symbol,
                date=date.to_pydatetime().date(),
                open=float(row["Open"]),
                high=float(row["High"]),
                low=float(row["Low"]),
                close=float(row["Close"]),
                volume=float(row["Volume"])
            )
            session.add(record)
        session.commit()
        print(f"📥 Stored historical data for {ticker_symbol} in DB")
        return data

    except Exception as e:
        print(f"❌ Error fetching historical data for {ticker_symbol}: {e}")
        return pd.DataFrame()
    finally:
        session.close()

def fetch_fundamental_metrics(ticker_symbol):
    session: Session = SessionLocal()
    today = datetime.today().date()
    try:
        # Check if data already exists in DB
        existing = session.query(Fundamental).filter(
            Fundamental.symbol == ticker_symbol,
            func.date(Fundamental.date) == today
        ).first()


        if existing:
            print(f"✅ Loaded fundamentals for {ticker_symbol} from DB")
            return {
                "marketCap": existing.market_cap,
                "ROCE": existing.roce,
                "PAT": existing.pat
            }

        # Fetch from yfinance
        ticker = yf.Ticker(f"{ticker_symbol}.NS")
        info = ticker.info
        if not info or "marketCap" not in info:
            return {"error": f"No fundamental data found for {ticker_symbol}.NS"}

        market_cap = info.get("marketCap", 0)
        roce = info.get("returnOnEquity", 0) * 100 if info.get("returnOnEquity") is not None else 0
        pat = info.get("netIncomeToCommon", 0) if info.get("netIncomeToCommon") is not None else 0

        metrics = {
            "marketCap": market_cap,
            "ROCE": roce,
            "PAT": pat
        }

        record = Fundamental(
            symbol=ticker_symbol,
            date=today,
            market_cap=market_cap,
            roce=roce,
            pat=pat
        )
        session.add(record)
        session.commit()
        print(f"📥 Stored fundamentals for {ticker_symbol} in DB")
        return metrics

    except Exception as e:
        print(f"❌ Error fetching fundamentals for {ticker_symbol}: {e}")
        return {"error": str(e)}
    finally:
        session.close()
