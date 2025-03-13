import './globals.css';

export const metadata = {
  title: 'GenericRx | Generic Medicine Alternative Intelligence',
  description: 'Map high-cost branded medicines to verified Jan Aushadhi generic alternatives and calculate monthly prescription savings.',
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body className="min-h-screen flex flex-col">
        <header className="bg-white border-b border-slate-200 sticky top-0 z-50">
          <div className="max-w-6xl mx-auto px-4 h-16 flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="bg-blue-600 text-white p-2 rounded-lg font-bold text-lg leading-none">
                Rx
              </div>
              <div>
                <span className="text-xl font-extrabold text-slate-900 tracking-tight">
                  Generic<span className="text-blue-600">Rx</span>
                </span>
                <span className="hidden sm:inline-block ml-2 text-xs bg-emerald-50 text-emerald-700 px-2 py-0.5 rounded-full font-medium border border-emerald-200">
                  Jan Aushadhi Intelligence
                </span>
              </div>
            </div>
            <div className="text-xs text-slate-500 font-medium">
              India Healthcare Savings Platform
            </div>
          </div>
        </header>

        <main className="flex-1 max-w-6xl w-full mx-auto px-4 py-8">
          {children}
        </main>

        <footer className="bg-white border-t border-slate-200 py-6 text-center text-xs text-slate-400">
          GenericRx — Comparing Active Salt Compositions and PMBJP Prices
        </footer>
      </body>
    </html>
  );
}