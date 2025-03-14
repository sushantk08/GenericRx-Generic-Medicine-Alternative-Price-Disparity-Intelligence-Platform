'use client';

import React from 'react';
import { CheckCircle2, TrendingDown, Plus, Sparkles, Building2 } from 'lucide-react';

export default function ComparisonCard({ data, onAddToCalculator }) {
  if (!data) return null;

  const { branded_medicine, best_alternative, max_savings_percentage } = data;

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* Savings Callout Header */}
      {best_alternative && max_savings_percentage > 0 && (
        <div className="bg-gradient-to-r from-emerald-600 to-teal-600 rounded-2xl p-4 sm:p-5 text-white shadow-md flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-white/20 backdrop-blur-sm rounded-xl">
              <TrendingDown className="w-6 h-6 text-white" />
            </div>
            <div>
              <div className="text-xl sm:text-2xl font-black flex items-center gap-2">
                <span>{max_savings_percentage.toFixed(1)}% Lower Cost</span>
                <span className="text-xs bg-white text-emerald-800 font-bold px-2 py-0.5 rounded-full uppercase tracking-wider">
                  Verified Alternative
                </span>
              </div>
              <p className="text-emerald-50 text-xs sm:text-sm font-medium">
                Switching saves <span className="font-bold underline decoration-white/40">₹{best_alternative.price_diff_per_unit.toFixed(2)}</span> on every single tablet.
              </p>
            </div>
          </div>

          <button
            onClick={() => onAddToCalculator && onAddToCalculator(branded_medicine)}
            className="w-full sm:w-auto inline-flex items-center justify-center px-4 py-2.5 bg-white text-emerald-800 hover:bg-emerald-50 rounded-xl font-bold text-sm shadow-sm transition active:scale-95"
          >
            <Plus className="w-4 h-4 mr-1.5" />
            Add to Savings Calculator
          </button>
        </div>
      )}

      {/* Side-by-Side Comparison Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Left: Branded Medicine */}
        <div className="bg-white border border-slate-200 rounded-2xl p-5 shadow-sm space-y-4 relative">
          <div className="flex justify-between items-start">
            <span className="text-xs font-bold text-slate-500 uppercase tracking-wider bg-slate-100 px-2.5 py-1 rounded-md">
              Prescribed Brand
            </span>
            <span className="text-xs text-slate-400 font-medium">Pack of {branded_medicine.pack_size}</span>
          </div>

          <div>
            <h3 className="text-lg font-bold text-slate-900 leading-snug">
              {branded_medicine.brand_name}
            </h3>
            {branded_medicine.manufacturer && (
              <p className="text-xs text-slate-500 flex items-center mt-1">
                <Building2 className="w-3.5 h-3.5 mr-1 text-slate-400" />
                {branded_medicine.manufacturer}
              </p>
            )}
          </div>

          {/* Salt Details */}
          <div className="p-3 bg-slate-50 rounded-xl border border-slate-100 text-xs space-y-1">
            <span className="text-slate-500 block">Active Chemical Salt:</span>
            <span className="font-semibold text-slate-800 block text-sm">
              {branded_medicine.salt_name} ({branded_medicine.strength_value} {branded_medicine.strength_unit})
            </span>
          </div>

          {/* Pricing */}
          <div className="pt-2 border-t border-slate-100 flex items-baseline justify-between">
            <div>
              <span className="text-xs text-slate-400 block">Maximum Retail Price</span>
              <span className="text-xl font-extrabold text-slate-800">
                ₹{branded_medicine.mrp.toFixed(2)}
              </span>
            </div>
            <div className="text-right">
              <span className="text-xs text-slate-400 block">Cost Per Unit</span>
              <span className="text-base font-bold text-slate-700">
                ₹{branded_medicine.price_per_unit.toFixed(2)} / tab
              </span>
            </div>
          </div>
        </div>

        {/* Right: Generic Equivalent (Jan Aushadhi) */}
        {best_alternative ? (
          <div className="bg-emerald-50/50 border-2 border-emerald-500/80 rounded-2xl p-5 shadow-sm space-y-4 relative">
            <div className="flex justify-between items-start">
              <span className="text-xs font-bold text-emerald-800 uppercase tracking-wider bg-emerald-100/80 px-2.5 py-1 rounded-md flex items-center gap-1">
                <Sparkles className="w-3.5 h-3.5 text-emerald-700" />
                Generic Equivalent
              </span>
              <span className="text-xs text-emerald-700 font-semibold bg-white border border-emerald-200 px-2 py-0.5 rounded-full">
                {best_alternative.source}
              </span>
            </div>

            <div>
              <h3 className="text-lg font-bold text-emerald-950 leading-snug">
                {best_alternative.generic_name}
              </h3>
              <p className="text-xs text-emerald-700 font-medium flex items-center mt-1">
                <CheckCircle2 className="w-3.5 h-3.5 mr-1 text-emerald-600" />
                100% Identical Active Chemical Composition
              </p>
            </div>

            {/* Salt Match Verification */}
            <div className="p-3 bg-white rounded-xl border border-emerald-200/80 text-xs space-y-1">
              <span className="text-emerald-700 block font-medium">Standardized Salt & Strength:</span>
              <span className="font-bold text-slate-900 block text-sm">
                {branded_medicine.salt_name} ({branded_medicine.strength_value} {branded_medicine.strength_unit})
              </span>
            </div>

            {/* Pricing */}
            <div className="pt-2 border-t border-emerald-200/60 flex items-baseline justify-between">
              <div>
                <span className="text-xs text-emerald-700 font-medium block">Jan Aushadhi Price</span>
                <span className="text-2xl font-black text-emerald-700">
                  ₹{best_alternative.mrp.toFixed(2)}
                </span>
              </div>
              <div className="text-right">
                <span className="text-xs text-emerald-700 font-medium block">Cost Per Unit</span>
                <span className="text-lg font-black text-emerald-800">
                  ₹{best_alternative.price_per_unit.toFixed(2)} / tab
                </span>
              </div>
            </div>
          </div>
        ) : (
          <div className="bg-slate-50 border border-dashed border-slate-300 rounded-2xl p-8 flex flex-col items-center justify-center text-center text-slate-500 space-y-2">
            <p className="text-sm font-medium">No generic equivalent indexed yet for this specific composition.</p>
          </div>
        )}
      </div>
    </div>
  );
}