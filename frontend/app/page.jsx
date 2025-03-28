'use client';

import React, { useState } from 'react';
import SearchBar from '../components/SearchBar';
import ComparisonCard from '../components/ComparisonCard';
import SavingsCalculator from '../components/SavingsCalculator';
import { Loader2 } from 'lucide-react';
import { API_BASE_URL } from '../utils/api';

export default function HomePage() {
  const [selectedMedicine, setSelectedMedicine] = useState(null);
  const [alternativesData, setAlternativesData] = useState(null);
  const [isLoadingAlternatives, setIsLoadingAlternatives] = useState(false);

  // Prescription basket for savings calculator
  const [prescriptionItems, setPrescriptionItems] = useState([]);

  const handleSelectMedicine = async (med) => {
    setSelectedMedicine(med);
    setIsLoadingAlternatives(true);
    setAlternativesData(null);

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/medicines/${med.id}/alternatives`);
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
    setPrescriptionItems((prev) => {
      const exists = prev.find((item) => item.medicine.id === medicine.id);
      if (exists) {
        return prev;
      }
      return [...prev, { medicine, tablets_per_day: 1.0 }];
    });
  };

  const handleRemoveFromCalculator = (medicineId) => {
    setPrescriptionItems((prev) => prev.filter((item) => item.medicine.id !== medicineId));
  };

  const handleUpdateDosage = (medicineId, newDosage) => {
    setPrescriptionItems((prev) =>
      prev.map((item) =>
        item.medicine.id === medicineId ? { ...item, tablets_per_day: newDosage } : item
      )
    );
  };

  return (
    <div className="space-y-8 pb-16">
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

      {/* Side-by-Side Comparison Card */}
      {alternativesData && !isLoadingAlternatives && (
        <ComparisonCard 
          data={alternativesData} 
          onAddToCalculator={handleAddToCalculator} 
        />
      )}

      {/* Interactive Monthly Prescription Savings Calculator */}
      <SavingsCalculator
        prescriptionItems={prescriptionItems}
        onRemoveItem={handleRemoveFromCalculator}
        onUpdateDosage={handleUpdateDosage}
      />
    </div>
  );
}