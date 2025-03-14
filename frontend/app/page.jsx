'use client';

import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import { Pill, ArrowRight } from 'lucide-react';

export default function HomePage() {
  const [selectedMedicine, setSelectedMedicine] = useState(null);

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="text-center max-w-2xl mx-auto space-y-3">
        <h1 className="text-3xl sm:text-4xl font-black text-slate-900 tracking-tight">
          Find Affordable Generic Medicines.
        </h1>
        <p className="text-slate-600 text-sm sm:text-base">
          Type your prescribed brand name to find approved Jan Aushadhi generic substitutes with the exact same chemical salt and up to 85% lower prices.
        </p>
      </div>

      {/* Autocomplete Search Bar */}
      <SearchBar onSelectMedicine={(med) => setSelectedMedicine(med)} />

      {/* Quick Selection Status */}
      {selectedMedicine && (
        <div className="max-w-2xl mx-auto p-4 bg-white border border-blue-100 rounded-xl shadow-sm flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="p-2.5 bg-blue-50 text-blue-600 rounded-lg">
              <Pill className="w-5 h-5" />
            </div>
            <div>
              <div className="font-semibold text-slate-900 text-sm">
                Selected: {selectedMedicine.brand_name}
              </div>
              <div className="text-xs text-slate-500">
                Active Salt: <span className="font-medium text-slate-700">{selectedMedicine.salt_name} ({selectedMedicine.strength})</span>
              </div>
            </div>
          </div>
          <div className="text-right text-xs text-blue-600 font-semibold flex items-center">
            Ready for Comparison
            <ArrowRight className="w-3.5 h-3.5 ml-1" />
          </div>
        </div>
      )}
    </div>
  );
}