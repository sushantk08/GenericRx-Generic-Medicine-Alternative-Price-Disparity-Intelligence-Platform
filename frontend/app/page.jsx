'use client';

import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import ComparisonCard from '../components/ComparisonCard';
import { Loader2 } from 'lucide-react';

export default function HomePage() {
  const [selectedMedicine, setSelectedMedicine] = useState(null);
  const [alternativesData, setAlternativesData] = useState(null);
  const [isLoadingAlternatives, setIsLoadingAlternatives] = useState(false);

  const handleSelectMedicine = async (med) => {
    setSelectedMedicine(med);
    setIsLoadingAlternatives(true);
    setAlternativesData(null);

    try {
      const res = await fetch(`http://localhost:8000/api/v1/medicines/${med.id}/alternatives`);
      if (res.ok) {
        const data = await res.json();
        setAlternativesData(data);
      }
    } catch (err) {
      console.error('Failed to fetch alternatives:', err);
    } finally {
      setIsLoadingAlternatives(false);
    }
  };

  const handleAddToCalculator = (medicine) => {
    alert(`Added ${medicine.brand_name} to Prescription Calculator! (Configured in Step 14.2)`);
  };

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
      <SearchBar onSelectMedicine={handleSelectMedicine} />

      {/* Loading Indicator */}
      {isLoadingAlternatives && (
        <div className="flex justify-center items-center py-8 text-blue-600">
          <Loader2 className="w-8 h-8 animate-spin" />
        </div>
      )}

      {/* Comparison Cards */}
      {alternativesData && !isLoadingAlternatives && (
        <ComparisonCard 
          data={alternativesData} 
          onAddToCalculator={handleAddToCalculator} 
        />
      )}
    </div>
  );
}