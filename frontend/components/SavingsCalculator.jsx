'use client';

import React, { useState, useEffect } from 'react';
import { Calculator, Trash2 } from 'lucide-react';
import { API_BASE_URL } from '../utils/api';

export default function SavingsCalculator({ prescriptionItems, onRemoveItem, onUpdateDosage }) {
  const [calculation, setCalculation] = useState(null);
  const [isCalculating, setIsCalculating] = useState(false);

  useEffect(() => {
    if (!prescriptionItems || prescriptionItems.length === 0) {
      setCalculation(null);
      return;
    }

    const fetchSavings = async () => {
      setIsCalculating(true);
      try {
        const payload = {
          items: prescriptionItems.map((item) => ({
            branded_medicine_id: item.medicine.id,
            tablets_per_day: parseFloat(item.tablets_per_day) || 1.0,
            days_per_month: 30,
          })),
        };

        const res = await fetch(`${API_BASE_URL}/api/v1/calculator/savings`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        });

        if (res.ok) {
          const data = await res.json();
          setCalculation(data);
        }
      } catch (err) {
        console.error('Calculation error:', err);
      } finally {
        setIsCalculating(false);
      }
    };

    fetchSavings();
  }, [prescriptionItems]);

  if (!prescriptionItems || prescriptionItems.length === 0) {
    return null;
  }

  return (
    <div className="w-full max-w-4xl mx-auto mt-10 space-y-6">
      <div className="flex items-center space-x-3">
        <div className="p-2.5 bg-blue-600 text-white rounded-xl">
          <Calculator className="w-6 h-6" />
        </div>
        <div>
          <h2 className="text-xl font-black text-slate-900">
            Monthly Prescription Savings Calculator
          </h2>
          <p className="text-xs sm:text-sm text-slate-500">
            Compare your ongoing monthly medicine expenditure with government generic substitutes.
          </p>
        </div>
      </div>

      {/* Summary Stat Cards */}
      {calculation && (
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
            <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider block">
              Current Branded Spend
            </span>
            <div className="text-2xl font-black text-slate-800 mt-1">
              ₹{calculation.total_branded_monthly_spend.toFixed(2)}
              <span className="text-xs text-slate-400 font-normal"> / month</span>
            </div>
          </div>

          <div className="bg-white border border-slate-200 rounded-2xl p-4 shadow-sm">
            <span className="text-xs font-semibold text-emerald-700 uppercase tracking-wider block">
              Jan Aushadhi Generic Spend
            </span>
            <div className="text-2xl font-black text-emerald-700 mt-1">
              ₹{calculation.total_generic_monthly_spend.toFixed(2)}
              <span className="text-xs text-emerald-600 font-normal"> / month</span>
            </div>
          </div>

          <div className="bg-emerald-600 rounded-2xl p-4 text-white shadow-md">
            <span className="text-xs font-semibold text-emerald-100 uppercase tracking-wider block flex items-center justify-between">
              Total Monthly Savings
              <span className="bg-white/20 text-white px-2 py-0.5 rounded-full text-[10px] font-bold">
                {calculation.overall_savings_percentage.toFixed(0)}% OFF
              </span>
            </span>
            <div className="text-2xl font-black text-white mt-1">
              ₹{calculation.total_monthly_savings.toFixed(2)}
              <span className="text-xs text-emerald-100 font-normal"> / month</span>
            </div>
            <div className="text-xs text-emerald-100 mt-1 font-medium">
              ≈ ₹{calculation.total_annual_savings.toFixed(2)} saved every year
            </div>
          </div>
        </div>
      )}

      {/* Prescription Items List */}
      <div className="bg-white border border-slate-200 rounded-2xl overflow-hidden shadow-sm">
        <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50 font-bold text-sm text-slate-700 flex justify-between">
          <span>Active Medications ({prescriptionItems.length})</span>
          <span className="text-xs text-slate-500 font-normal">Based on standard 30-day monthly cycle</span>
        </div>

        <div className="divide-y divide-slate-100">
          {prescriptionItems.map((item) => (
            <div key={item.medicine.id} className="p-4 sm:p-5 flex flex-col sm:flex-row sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <div className="font-bold text-slate-900 text-base">
                  {item.medicine.brand_name}
                </div>
                <div className="text-xs text-slate-500">
                  Active Salt: <span className="font-medium text-slate-700">{item.medicine.salt_name} ({item.medicine.strength_value} {item.medicine.strength_unit})</span>
                </div>
              </div>

              <div className="flex items-center space-x-4">
                {/* Dosage Selector */}
                <div className="flex items-center space-x-2">
                  <label className="text-xs text-slate-500 font-medium">Dose:</label>
                  <select
                    value={item.tablets_per_day}
                    onChange={(e) => onUpdateDosage(item.medicine.id, parseFloat(e.target.value))}
                    className="text-xs font-semibold bg-slate-50 border border-slate-200 rounded-lg px-2.5 py-1.5 focus:outline-none focus:ring-1 focus:ring-blue-500"
                  >
                    <option value={0.5}>0.5 tab / day</option>
                    <option value={1.0}>1 tab / day</option>
                    <option value={2.0}>2 tabs / day</option>
                    <option value={3.0}>3 tabs / day</option>
                  </select>
                </div>

                {/* Remove Button */}
                <button
                  onClick={() => onRemoveItem(item.medicine.id)}
                  className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition"
                  title="Remove medicine"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}