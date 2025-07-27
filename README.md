# 📊 Backtesting Platform for Equity-Based Strategies

A full-stack application to backtest custom equity strategies using fundamental and price data of Indian stocks. Built with **FastAPI**, **PostgreSQL**, **React**, and **Tailwind CSS**.

---

## 🚀 Features

- Define backtest parameters: date range, rebalance frequency, portfolio size, capital
- Apply filters: Market Cap, ROCE, PAT (real PAT values from Yahoo Finance)
- Rank stocks using custom logic (e.g., ROCE descending)
- Position sizing: Equal, Market Cap Weighted, ROCE Weighted
- View:
  - 📈 Equity Curve
  - 📉 Drawdown Chart
  - 📊 Performance Metrics (CAGR, Sharpe Ratio, Max Drawdown)
  - 🏆 Top Winners & Losers
  - 📋 Portfolio Logs
- Export results as **CSV** or **Excel**
- Loading indicator while backtest is running

---

## 🛠️ Technologies Used

| Layer     | Technology              |
|-----------|-------------------------|
| Frontend  | React.js + Tailwind CSS |
| Backend   | FastAPI (Python)        |
| Database  | PostgreSQL              |
| Data      | Yahoo Finance (via `yfinance`) 
| ORM       | SQLAlchemy              |

---

## 🧰 Setup Instructions

1. Clone the Repository
git clone https://github.com/your-username/backtesting-platform.git
cd backtesting-platform

2. Set Up the Backend
cd backend
python -m venv venv
source venv/bin/activate  # or venv\\Scripts\\activate on Windows
pip install -r requirements.txt

3. Configure PostgreSQL
Create a database named backtesting_db
Update DATABASE_URL in database.py if needed

4. Run Backend Server
uvicorn main:app --reload

---

## 🌐 Frontend Setup

1. Install Dependencies
Make sure you have Node.js installed. Then run:
npm install
npx create-react-app my-app

2. Navigate to the Frontend Directory
cd my-app/

3. Start the Development Server
npm start

**The app will run on http://localhost:3000 and connect to the FastAPI backend at http://localhost:8000.**

---

## 🧪 Usage Guide

📈 Step 1: Configure Backtest Parameters

Use the form to input:

	a)Start Date and End Date
	b)Rebalance Frequency (Monthly, Quarterly, Yearly)
	c)Portfolio Size (e.g., Top 10 stocks)
	d)Initial Capital (e.g., ₹10,00,000)
	e)Filters:
		Market Cap Range
		ROCE Threshold
		PAT > 0 (optional)
	f)Ranking Logic (e.g., ROCE descending)
	g)Position Sizing Method:
		Equal Weight
		Market Cap Weighted
		ROCE Weighted
	
📈 Step 2: Run Backtest
Click Run Backtest to initiate the process. The frontend sends a POST request to the backend with your parameters.

📈 Step 3: View Results

Once the backtest completes, you’ll see:

	Performance Metrics: CAGR, Sharpe Ratio, Max Drawdown
	Equity Curve and Drawdown Chart
	Top Winners & Losers by actual return
	Portfolio Logs (last 5 entries)
	
📥 Step 4: Export Results

Download the full portfolio logs:

	Download CSV
	Download Excel

---

## 📁 File Structure

project-root/
│
├── backend/
│   ├── main.py                			# FastAPI app with /backtest and download endpoints
│   ├── fetch_yahoo.py         			# Yahoo Finance data fetch logic
│   ├── models.py              			# SQLAlchemy models for StockPrice and Fundamental
│   ├── database.py            			# DB connection and session setup
│   └── requirements.txt       			# Python dependencies
│
├── my-app/
│   ├── src
│ 	│ 	├──	App.js                      # Main React component
│   │   └──components/
│   │  			 └── BacktestForm.js    # Form for user input
│   └── package.json           			# Frontend dependencies
│			
└── README.md                  			# Project documentation (this file)