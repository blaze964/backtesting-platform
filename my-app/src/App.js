import React, { useState } from 'react';
import BacktestForm from './components/BacktestForm';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ResponsiveContainer
} from 'recharts';


export default function App() {

  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);

  const runBacktest = async (params) => {
    setLoading(true);
    setResults(null);
    try {
      const response = await fetch('http://localhost:8000/backtest', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(params),
      });
      const data = await response.json();
      setResults(data);
    } catch (error) {
      console.error('Backtest failed:', error);
      setResults({ error: 'Failed to connect to backend.' });
    }finally {
    setLoading(false);
  }
  };

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <h1 className="text-2xl font-bold mb-4">Backtest Configuration</h1>
      <BacktestForm onRun={runBacktest} />

      {loading && (
        <div className="mt-8 text-blue-600 font-semibold animate-pulse">
          ⏳ Running backtest... Please wait.
        </div>
      )}

      {results && results.error ? (
        <div className="mt-8 text-red-600 font-semibold">
          ⚠️ {results.error}
        </div>
      ) : results && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-2">Performance Metrics</h2>
          
          <h2 className="text-lg font-semibold mb-2">Equity Curve</h2>
          <div className="w-full h-64 mb-6">
            <ResponsiveContainer>
              <LineChart data={results.equityCurve}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="Date" tick={{ fontSize: 10 }} />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="Cumulative" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <h2 className="text-lg font-semibold mb-2">Drawdown Chart</h2>
          <div className="w-full h-64 mb-6">
            <ResponsiveContainer>
              <LineChart data={results.drawdown}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="Date" tick={{ fontSize: 10 }} />
                <YAxis domain={[-1, 0]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} />
                <Tooltip formatter={(v) => `${(v * 100).toFixed(2)}%`} />
                <Line type="monotone" dataKey="Drawdown" stroke="#ef4444" strokeWidth={2} name="Current Drawdown" />
                <Line type="monotone" dataKey="Returns" stroke="#000000" strokeWidth={1.5} name="Returns" />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <ul className="mb-4">
            {Object.entries(results.metrics).map(([k, v]) => (
              <li key={k}><strong>{k}:</strong> {v}</li>
            ))}
          </ul>

          {/* <h2 className="text-lg font-semibold">Top Winners</h2>
          <ul className="mb-4">
            {results.winners.map((w, i) => (
              <li key={i}>{w.symbol}: ROCE {w.ROCE.toFixed(2)}%</li>
            ))}
          </ul>

          <h2 className="text-lg font-semibold">Top Losers</h2>
          <ul className="mb-4">
            {results.losers.map((l, i) => (
              <li key={i}>{l.symbol}: ROCE {l.ROCE.toFixed(2)}%</li>
            ))}
          </ul> */}
          <h2 className="text-lg font-semibold">Top Winners</h2>
          <ul className="mb-4">
            {results.winners.map((w, i) => (
              <li key={i}>{w.symbol}: Return {w.return.toFixed(2)}%</li>
            ))}
          </ul>

          <h2 className="text-lg font-semibold">Top Losers</h2>
          <ul className="mb-4">
            {results.losers.map((l, i) => (
              <li key={i}>{l.symbol}: Return {l.return.toFixed(2)}%</li>
            ))}
          </ul>


          <h2 className="text-lg font-semibold">Portfolio Logs (Last 5)</h2>
          <table className="table-auto w-full border mt-2">
            <thead>
              <tr className="bg-gray-200">
                <th className="border px-2 py-1">Date</th>
                <th className="border px-2 py-1">Symbol</th>
                <th className="border px-2 py-1">Close</th>
                <th className="border px-2 py-1">Value</th>                
                <th className="border px-2 py-1">Weight</th>
                <th className="border px-2 py-1">Returns (%)</th>
              </tr>
            </thead>
            <tbody>
              {results.logs.map((log, i) => (
                <tr key={i}>
                  {/* <td className="border px-2 py-1">{log.Date}</td> */}
                  <td className="border px-2 py-1">
                    {new Date(log.Date).toLocaleDateString('en-IN', {
                      day: '2-digit',
                      month: 'short',
                      year: 'numeric'
                    })}
                  </td>
                  <td className="border px-2 py-1">{log.Symbol}</td>
                  <td className="border px-2 py-1">{log.Close.toFixed(2)}</td>
                  <td className="border px-2 py-1">{log.Value.toFixed(2)}</td>
                  <td className="border px-2 py-1">{typeof log.Weight === 'number' ? log.Weight.toFixed(4) : 'N/A'}</td>
                  <td className="border px-2 py-1">{typeof log.Returns === 'number' ? log.Returns.toFixed(2) : 'N/A'}</td>
                </tr>
              ))}
            </tbody>
          </table>

          <div className="mt-4 space-x-4">
            <a
              href="http://localhost:8000/download/csv"
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">Download CSV</a>

             <a
              href="http://localhost:8000/download/excel"
              className="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded">Download Excel</a>
          </div>
        </div>
      )}
    </div>
  );
}
