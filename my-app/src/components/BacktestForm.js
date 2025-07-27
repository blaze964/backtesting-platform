import React, { useState } from 'react';

export default function BacktestForm({ onRun }) {
  const [params, setParams] = useState({
    startDate: '',
    endDate: '',
    frequency: 'Monthly',
    portfolioSize: 10,
    capital: 1000000,
    marketCapMin: '',
    marketCapMax: '',
    roce: '',
    pat: false,
    rankingLogic: '',
    sizingMethod: 'Equal Weight',
  });

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setParams({
      ...params,
      [name]: type === 'checkbox' ? checked : value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onRun(params);
  };

  return (
    <form onSubmit={handleSubmit} className="grid grid-cols-2 gap-4">
      <div>
        <label>Start Date</label>
        <input type="date" name="startDate" value={params.startDate} onChange={handleChange} className="border p-2 w-full" />
      </div>
      <div>
        <label>End Date</label>
        <input type="date" name="endDate" value={params.endDate} onChange={handleChange} className="border p-2 w-full" />
      </div>
      <div>
        <label>Rebalance Frequency</label>
        <select name="frequency" value={params.frequency} onChange={handleChange} className="border p-2 w-full">
          <option>Monthly</option>
          <option>Quarterly</option>
          <option>Yearly</option>
        </select>
      </div>
      <div>
        <label>Portfolio Size</label>
        <input type="number" name="portfolioSize" value={params.portfolioSize} onChange={handleChange} className="border p-2 w-full" />
      </div>
      <div>
        <label>Initial Capital</label>
        <input type="number" name="capital" value={params.capital} onChange={handleChange} className="border p-2 w-full" />
      </div>
      <div>
        <label>Market Cap Min</label>
        <input type="number" name="marketCapMin" value={params.marketCapMin} onChange={handleChange} className="border p-2 w-full" />
      </div>
      <div>
        <label>Market Cap Max</label>
        <input type="number" name="marketCapMax" value={params.marketCapMax} onChange={handleChange} className="border p-2 w-full" />
      </div>
      <div>
        <label>ROCE &gt; (%)</label>
        <input type="number" name="roce" value={params.roce} onChange={handleChange} className="border p-2 w-full" />
      </div>
      <div className="flex items-center">
        <input type="checkbox" name="pat" checked={params.pat} onChange={handleChange} className="mr-2" />
        <label>PAT &gt; 0</label>
      </div>
      <div>
        <label>Ranking Logic</label>
        <input type="text" name="rankingLogic" value={params.rankingLogic} onChange={handleChange} className="border p-2 w-full" />
      </div>
      <div>
        <label>Position Sizing</label>
        <select name="sizingMethod" value={params.sizingMethod} onChange={handleChange} className="border p-2 w-full">
          <option>Equal Weight</option>
          <option>Market Cap Weighted</option>
          <option>ROCE Weighted</option>
        </select>
      </div>
      <div className="col-span-2">
        <button type="submit" className="bg-blue-600 text-white px-4 py-2 rounded w-full">
          Run Backtest
        </button>
      </div>
    </form>
  );
}
