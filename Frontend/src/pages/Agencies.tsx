import { useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExternalLink, Star, Phone, MapPin, Globe, Search, ChevronDown } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { AGENCIES_BY_STATE, ALL_STATES, getAllAgencies } from '../data/agencies';

export default function Agencies() {
  const [darkMode,      setDarkMode]      = useState(true);
  const [search,        setSearch]        = useState('');
  const [selectedState, setSelectedState] = useState('All States');
  const [expandedState, setExpandedState] = useState<string | null>(null);

  const allAgencies = useMemo(() => getAllAgencies(), []);

  const filtered = useMemo(() => {
    if (selectedState === 'All States') {
      if (!search) return null; // show by state groups
      return allAgencies.filter(a =>
        a.name.toLowerCase().includes(search.toLowerCase()) ||
        a.city.toLowerCase().includes(search.toLowerCase()) ||
        a.speciality.some(s => s.toLowerCase().includes(search.toLowerCase()))
      );
    }
    const stateAgencies = AGENCIES_BY_STATE[selectedState] || [];
    if (!search) return stateAgencies;
    return stateAgencies.filter(a =>
      a.name.toLowerCase().includes(search.toLowerCase()) ||
      a.city.toLowerCase().includes(search.toLowerCase()) ||
      a.speciality.some(s => s.toLowerCase().includes(search.toLowerCase()))
    );
  }, [selectedState, search, allAgencies]);

  const card = (agency: typeof allAgencies[0], i: number) => (
    <motion.div key={agency.name + agency.city}
      initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
      transition={{ delay: i * 0.03 }}
      className="rounded-2xl p-5 flex flex-col gap-3 transition-all hover:-translate-y-1"
      style={{ background: darkMode ? 'rgba(255,255,255,0.04)' : 'white', border: darkMode ? '1px solid rgba(255,255,255,0.08)' : '1px solid #e5e7eb', boxShadow: darkMode ? 'none' : '0 1px 4px rgba(0,0,0,0.06)' }}>
      <div className="flex items-start justify-between gap-2">
        <div>
          <h3 className={`font-bold text-base leading-tight ${darkMode ? 'text-white' : 'text-gray-900'}`}>{agency.name}</h3>
          <div className="flex items-center gap-1 mt-1">
            <MapPin size={11} className="text-emerald-400" />
            <span className={`text-xs ${darkMode ? 'text-white/50' : 'text-gray-500'}`}>{agency.city}, {agency.state}</span>
          </div>
        </div>
        <div className="flex items-center gap-1 px-2 py-1 rounded-lg flex-shrink-0"
          style={{ background: 'rgba(251,191,36,0.1)' }}>
          <Star size={11} className="text-amber-400 fill-amber-400" />
          <span className="text-amber-400 text-xs font-bold">{agency.rating}</span>
        </div>
      </div>

      <p className={`text-xs leading-relaxed ${darkMode ? 'text-white/60' : 'text-gray-600'}`}>{agency.description}</p>

      <div className="flex flex-wrap gap-1">
        {agency.speciality.slice(0, 3).map(s => (
          <span key={s} className="px-2 py-0.5 rounded-full text-[10px] font-medium"
            style={{ background: 'rgba(16,185,129,0.1)', color: '#34d399', border: '1px solid rgba(16,185,129,0.2)' }}>
            {s}
          </span>
        ))}
      </div>

      <div className={`text-xs ${darkMode ? 'text-white/40' : 'text-gray-400'}`}>
        From <span className="font-semibold text-emerald-400">{agency.budget}</span>
      </div>

      <div className="flex gap-2 mt-auto pt-1">
        {agency.phone && (
          <a href={`tel:${agency.phone}`}
            className={`flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-medium flex-1 justify-center border transition-colors ${darkMode ? 'bg-white/5 border-white/10 text-white/70 hover:bg-white/10' : 'bg-gray-50 border-gray-200 text-gray-600 hover:bg-gray-100'}`}>
            <Phone size={11} /> Call
          </a>
        )}
        <a href={agency.website} target="_blank" rel="noopener noreferrer"
          className="flex items-center gap-1 px-3 py-1.5 rounded-xl text-xs font-medium text-white flex-1 justify-center"
          style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
          <ExternalLink size={11} /> Visit
        </a>
      </div>
    </motion.div>
  );

  const bg = darkMode ? 'bg-[#020817] text-white' : 'bg-gray-50 text-gray-900';

  return (
    <div className={`min-h-screen flex flex-col ${bg}`}>
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
      <main className="flex-grow pt-28 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-8">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-3 text-sm font-medium"
            style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', color: '#34d399' }}>
            <Globe size={13} /> Travel Agencies Across India
          </div>
          <h1 className="font-playfair text-4xl font-bold mb-2">Find Travel Agencies</h1>
          <p className={`text-sm max-w-lg mx-auto ${darkMode ? 'text-white/50' : 'text-gray-500'}`}>
            {allAgencies.length}+ curated agencies across {ALL_STATES.length} states — compare ratings, packages & contact details
          </p>
        </motion.div>

        {/* Search + State filter */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <div className="relative flex-1">
            <Search size={15} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
            <input type="text" placeholder="Search agencies, cities, specialities…"
              value={search} onChange={e => setSearch(e.target.value)}
              className={`w-full pl-10 pr-4 py-3 rounded-xl text-sm outline-none ${darkMode ? 'text-white placeholder:text-white/30' : 'text-gray-900 placeholder:text-gray-400'}`}
              style={{ background: darkMode ? 'rgba(255,255,255,0.06)' : 'white', border: darkMode ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e5e7eb' }} />
          </div>
          <select value={selectedState} onChange={e => setSelectedState(e.target.value)}
            className="px-4 py-3 rounded-xl text-sm outline-none cursor-pointer min-w-[180px]"
            style={{
              background: darkMode ? '#0f172a' : 'white',
              border: darkMode ? '1px solid rgba(255,255,255,0.15)' : '1px solid #e5e7eb',
              color: darkMode ? 'white' : '#111827',
              colorScheme: darkMode ? 'dark' : 'light',
            }}>
            <option value="All States" style={{ background: darkMode ? '#0f172a' : 'white', color: darkMode ? 'white' : '#111827' }}>All States</option>
            {ALL_STATES.map(s => (
              <option key={s} value={s} style={{ background: darkMode ? '#0f172a' : 'white', color: darkMode ? 'white' : '#111827' }}>{s}</option>
            ))}
          </select>
        </div>

        {/* Search results */}
        {(search || selectedState !== 'All States') && filtered && (
          <>
            <p className={`text-sm mb-5 ${darkMode ? 'text-white/40' : 'text-gray-400'}`}>{filtered.length} results</p>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {filtered.map((a, i) => card(a, i))}
            </div>
            {filtered.length === 0 && (
              <div className="text-center py-20">
                <p className={darkMode ? 'text-white/40' : 'text-gray-400'}>No agencies found for "{search}"</p>
              </div>
            )}
          </>
        )}

        {/* State-wise accordion (default view) */}
        {!search && selectedState === 'All States' && (
          <div className="space-y-4">
            {ALL_STATES.map(state => (
              <div key={state} className="rounded-2xl overflow-hidden"
                style={{ border: darkMode ? '1px solid rgba(255,255,255,0.08)' : '1px solid #e5e7eb' }}>
                {/* State header */}
                <button onClick={() => setExpandedState(expandedState === state ? null : state)}
                  className={`w-full flex items-center justify-between px-5 py-4 font-semibold text-left transition-colors ${darkMode ? 'bg-white/4 hover:bg-white/6 text-white' : 'bg-gray-50 hover:bg-gray-100 text-gray-900'}`}
                  style={{ background: expandedState === state ? (darkMode ? 'rgba(16,185,129,0.08)' : 'rgba(16,185,129,0.05)') : undefined }}>
                  <div className="flex items-center gap-3">
                    <span className="text-emerald-400">📍</span>
                    <span>{state}</span>
                    <span className={`text-xs px-2 py-0.5 rounded-full ${darkMode ? 'bg-white/10 text-white/50' : 'bg-gray-200 text-gray-500'}`}>
                      {AGENCIES_BY_STATE[state]?.length || 0} agencies
                    </span>
                  </div>
                  <ChevronDown size={18} className={`transition-transform ${expandedState === state ? 'rotate-180 text-emerald-400' : darkMode ? 'text-white/40' : 'text-gray-400'}`} />
                </button>

                {/* Agencies grid */}
                <AnimatePresence>
                  {expandedState === state && (
                    <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.3 }}>
                      <div className={`p-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4 ${darkMode ? 'bg-white/2' : 'bg-white'}`}
                        style={{ background: darkMode ? 'rgba(255,255,255,0.02)' : 'white' }}>
                        {(AGENCIES_BY_STATE[state] || []).map((a, i) => card({ ...a, state }, i))}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            ))}
          </div>
        )}
      </main>
      <Footer />
    </div>
  );
}
