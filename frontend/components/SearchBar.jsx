'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Search, Pill, Building2, Loader2, X } from 'lucide-react';
import { API_BASE_URL } from '../utils/api';

export default function SearchBar({ onSelectMedicine }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown on outside click
  useEffect(() => {
    function handleClickOutside(event) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Debounced API call to autocomplete endpoint
  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      setIsLoading(false);
      return;
    }

    const timer = setTimeout(async () => {
      setIsLoading(true);
      try {
        const response = await fetch(
          `${API_BASE_URL}/api/v1/medicines/autocomplete?q=${encodeURIComponent(query)}&limit=8`
        );
        if (response.ok) {
          const data = await response.json();
          setResults(data);
          setIsOpen(true);
        }
      } catch (error) {
        console.error('Error fetching autocomplete:', error);
      } finally {
        setIsLoading(false);
      }
    }, 200);

    return () => clearTimeout(timer);
  }, [query]);

  const handleSelect = (medicine) => {
    setQuery(medicine.brand_name);
    setIsOpen(false);
    if (onSelectMedicine) {
      onSelectMedicine(medicine);
    }
  };

  const handleClear = () => {
    setQuery('');
    setResults([]);
    setIsOpen(false);
  };

  return (
    <div className="relative w-full max-w-2xl mx-auto" ref={dropdownRef}>
      {/* Search Input Bar */}
      <div className="relative flex items-center shadow-sm">
        <div className="absolute left-4 text-slate-400 pointer-events-none">
          <Search className="w-5 h-5" />
        </div>
        <input
          type="text"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onFocus={() => query.trim() && setResults.length > 0 && setIsOpen(true)}
          placeholder="Type branded medicine (e.g. Telma 40, Glycomet 500, Pan 40)..."
          className="w-full pl-12 pr-12 py-3.5 bg-white border border-slate-300 rounded-xl text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base font-medium transition"
        />
        {isLoading && (
          <div className="absolute right-4 text-blue-600 animate-spin">
            <Loader2 className="w-5 h-5" />
          </div>
        )}
        {!isLoading && query && (
          <button
            onClick={handleClear}
            className="absolute right-4 text-slate-400 hover:text-slate-600 transition"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* Autocomplete Suggestions Dropdown */}
      {isOpen && results.length > 0 && (
        <div className="absolute left-0 right-0 mt-2 bg-white border border-slate-200 rounded-xl shadow-xl overflow-hidden z-50 divide-y divide-slate-100 max-h-96 overflow-y-auto">
          {results.map((med) => (
            <div
              key={med.id}
              onClick={() => handleSelect(med)}
              className="p-3.5 hover:bg-blue-50/70 cursor-pointer transition flex items-center justify-between group"
            >
              <div className="space-y-1">
                <div className="flex items-center space-x-2">
                  <span className="font-semibold text-slate-900 group-hover:text-blue-600 text-sm sm:text-base">
                    {med.brand_name}
                  </span>
                  <span className="text-xs bg-slate-100 text-slate-600 px-2 py-0.5 rounded font-mono font-medium">
                    {med.dosage_form}
                  </span>
                </div>
                <div className="flex items-center space-x-2 text-xs text-slate-500">
                  <span className="flex items-center text-blue-700 font-medium bg-blue-50 px-1.5 py-0.5 rounded">
                    <Pill className="w-3 h-3 mr-1 inline" />
                    {med.salt_name} ({med.strength})
                  </span>
                  {med.manufacturer && (
                    <span className="hidden sm:inline-flex items-center text-slate-400">
                      <Building2 className="w-3 h-3 mr-1 inline" />
                      {med.manufacturer}
                    </span>
                  )}
                </div>
              </div>

              <div className="text-right">
                <div className="text-sm font-bold text-slate-800">
                  ₹{med.mrp.toFixed(2)}
                </div>
                <div className="text-xs text-slate-500">
                  ₹{med.price_per_unit.toFixed(2)} / tab
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}