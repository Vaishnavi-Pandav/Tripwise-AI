import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MapPin, Calendar, Users, DollarSign,
  Sparkles, ArrowRight, Plane, AlertCircle, Map,
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import RouteMapModal from '../components/RouteMapModal';
import { generateTripPlan, type TripGenerationRequest } from '../services/api';

// ── Markdown renderer ─────────────────────────────────────────────────────────
// Converts the markdown returned by the AI into styled JSX without extra deps.

function renderMarkdown(text: string): JSX.Element {
  const lines = text.split('\n');
  const elements: JSX.Element[] = [];
  let keyIdx = 0;
  let tableBuffer: string[] = [];

  const flushTable = () => {
    if (tableBuffer.length < 2) {
      tableBuffer = [];
      return;
    }
    const [headerRow, , ...bodyRows] = tableBuffer;
    const headers = headerRow.split('|').map(c => c.trim()).filter(Boolean);
    const rows = bodyRows
      .filter(r => r.trim() && !r.match(/^[\s|:-]+$/))
      .map(r => r.split('|').map(c => c.trim()).filter(Boolean));

    elements.push(
      <div key={keyIdx++} className="overflow-x-auto my-4">
        <table className="w-full text-sm border-collapse">
          <thead>
            <tr className="border-b border-white/20">
              {headers.map((h, i) => (
                <th key={i} className="py-2 px-3 text-left text-emerald-400 font-semibold">
                  {h.replace(/\*\*/g, '')}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {rows.map((row, ri) => (
              <tr key={ri} className="border-b border-white/10 hover:bg-white/5 transition-colors">
                {row.map((cell, ci) => (
                  <td key={ci} className="py-2 px-3 text-white/80">
                    {cell.replace(/\*\*/g, '')}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
    tableBuffer = [];
  };

  const inlineFormat = (str: string) => {
    // Bold **text**
    return str.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Table row
    if (line.trim().startsWith('|')) {
      tableBuffer.push(line);
      continue;
    } else if (tableBuffer.length > 0) {
      flushTable();
    }

    // H2
    if (line.startsWith('## ')) {
      elements.push(
        <h2
          key={keyIdx++}
          className="text-xl font-bold text-white mt-8 mb-3 pb-2 border-b border-white/10 flex items-center gap-2"
          dangerouslySetInnerHTML={{ __html: inlineFormat(line.replace('## ', '')) }}
        />
      );
      continue;
    }

    // H3
    if (line.startsWith('### ')) {
      elements.push(
        <h3
          key={keyIdx++}
          className="text-base font-semibold text-emerald-400 mt-5 mb-2"
          dangerouslySetInnerHTML={{ __html: inlineFormat(line.replace('### ', '')) }}
        />
      );
      continue;
    }

    // H1
    if (line.startsWith('# ')) {
      elements.push(
        <h1
          key={keyIdx++}
          className="text-2xl font-bold text-white mt-6 mb-4"
          dangerouslySetInnerHTML={{ __html: inlineFormat(line.replace('# ', '')) }}
        />
      );
      continue;
    }

    // Bullet
    if (line.match(/^[-*] /)) {
      elements.push(
        <li
          key={keyIdx++}
          className="flex items-start gap-2 text-white/75 text-sm py-0.5 ml-2"
        >
          <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" />
          <span dangerouslySetInnerHTML={{ __html: inlineFormat(line.replace(/^[-*] /, '')) }} />
        </li>
      );
      continue;
    }

    // Numbered list
    if (line.match(/^\d+\. /)) {
      elements.push(
        <li
          key={keyIdx++}
          className="flex items-start gap-2 text-white/75 text-sm py-0.5 ml-2"
        >
          <span className="text-emerald-400 font-semibold flex-shrink-0 min-w-[1.2rem]">
            {line.match(/^(\d+)\./)?.[1]}.
          </span>
          <span dangerouslySetInnerHTML={{ __html: inlineFormat(line.replace(/^\d+\. /, '')) }} />
        </li>
      );
      continue;
    }

    // Horizontal rule
    if (line.match(/^---+$/)) {
      elements.push(<hr key={keyIdx++} className="border-white/10 my-4" />);
      continue;
    }

    // Empty line
    if (line.trim() === '') {
      elements.push(<div key={keyIdx++} className="h-1" />);
      continue;
    }

    // Regular paragraph
    elements.push(
      <p
        key={keyIdx++}
        className="text-white/75 text-sm leading-relaxed"
        dangerouslySetInnerHTML={{ __html: inlineFormat(line) }}
      />
    );
  }

  // Flush any remaining table
  if (tableBuffer.length > 0) flushTable();

  return <>{elements}</>;
}

// ── Component ─────────────────────────────────────────────────────────────────

interface FormData {
  source: string;
  destination: string;
  days: string;
  travelers: string;
  budget: string;
}

const Results = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [form, setForm] = useState<FormData>({
    source: '',
    destination: '',
    days: '',
    travelers: '',
    budget: '',
  });
  const [loading, setLoading] = useState(false);
  const [itinerary, setItinerary] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [showRouteMap, setShowRouteMap] = useState(false);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setForm(prev => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setItinerary(null);
    setLoading(true);

    const payload: TripGenerationRequest = {
      source: form.source.trim(),
      destination: form.destination.trim(),
      days: parseInt(form.days),
      travelers: parseInt(form.travelers),
      budget: parseFloat(form.budget),
    };

    try {
      const result = await generateTripPlan(payload);
      setItinerary(result.itinerary);
    } catch (err: unknown) {
      const message =
        err instanceof Error ? err.message : 'Something went wrong. Please try again.';
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  const isFormValid =
    form.source && form.destination && form.days && form.travelers && form.budget;

  return (
    <div className="min-h-screen flex flex-col bg-[#020817] text-white">
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

      <main className="flex-grow pt-28 pb-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-4xl mx-auto">

          {/* ── Page header ── */}
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center mb-10"
          >
            <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-4 text-sm font-medium"
              style={{ background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', color: '#34d399' }}>
              <Sparkles size={14} />
              Powered by Gemini AI
            </div>
            <h1 className="font-playfair text-4xl sm:text-5xl font-bold text-white mb-3">
              Plan Your Dream Trip
            </h1>
            <p className="text-white/50 text-base max-w-md mx-auto">
              Tell us where you want to go and we'll craft a personalised itinerary in seconds.
            </p>
          </motion.div>

          {/* ── Trip form ── */}
          <motion.form
            onSubmit={handleSubmit}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="rounded-2xl p-6 sm:p-8 mb-8"
            style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}
          >
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-5">

              {/* Source */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-white/50 flex items-center gap-1.5">
                  <Plane size={12} className="text-emerald-400" /> Travelling From
                </label>
                <input
                  type="text"
                  name="source"
                  value={form.source}
                  onChange={handleChange}
                  placeholder="e.g. Mumbai"
                  required
                  className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder:text-white/30 outline-none transition-all focus:ring-2 focus:ring-emerald-500/50"
                  style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              {/* Destination */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-white/50 flex items-center gap-1.5">
                  <MapPin size={12} className="text-emerald-400" /> Destination
                </label>
                <input
                  type="text"
                  name="destination"
                  value={form.destination}
                  onChange={handleChange}
                  placeholder="e.g. Bali, Indonesia"
                  required
                  className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder:text-white/30 outline-none transition-all focus:ring-2 focus:ring-emerald-500/50"
                  style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              {/* Days */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-white/50 flex items-center gap-1.5">
                  <Calendar size={12} className="text-emerald-400" /> Duration (days)
                </label>
                <input
                  type="number"
                  name="days"
                  value={form.days}
                  onChange={handleChange}
                  placeholder="e.g. 7"
                  min={1}
                  max={30}
                  required
                  className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder:text-white/30 outline-none transition-all focus:ring-2 focus:ring-emerald-500/50"
                  style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              {/* Travelers */}
              <div className="flex flex-col gap-1.5">
                <label className="text-xs font-semibold uppercase tracking-wider text-white/50 flex items-center gap-1.5">
                  <Users size={12} className="text-emerald-400" /> Travelers
                </label>
                <input
                  type="number"
                  name="travelers"
                  value={form.travelers}
                  onChange={handleChange}
                  placeholder="e.g. 2"
                  min={1}
                  required
                  className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder:text-white/30 outline-none transition-all focus:ring-2 focus:ring-emerald-500/50"
                  style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>

              {/* Budget — full width */}
              <div className="flex flex-col gap-1.5 sm:col-span-2">
                <label className="text-xs font-semibold uppercase tracking-wider text-white/50 flex items-center gap-1.5">
                  <DollarSign size={12} className="text-emerald-400" /> Total Budget (USD)
                </label>
                <input
                  type="number"
                  name="budget"
                  value={form.budget}
                  onChange={handleChange}
                  placeholder="e.g. 2000"
                  min={1}
                  required
                  className="w-full px-4 py-3 rounded-xl text-sm text-white placeholder:text-white/30 outline-none transition-all focus:ring-2 focus:ring-emerald-500/50"
                  style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}
                />
              </div>
            </div>

            {/* Submit */}
            <motion.button
              type="submit"
              disabled={!isFormValid || loading}
              whileHover={isFormValid && !loading ? { scale: 1.02 } : {}}
              whileTap={isFormValid && !loading ? { scale: 0.98 } : {}}
              className="mt-6 w-full py-4 rounded-xl font-semibold text-white flex items-center justify-center gap-2 transition-all"
              style={{
                background: isFormValid && !loading
                  ? 'linear-gradient(135deg, #10b981, #0ea5e9)'
                  : 'rgba(255,255,255,0.08)',
                cursor: isFormValid && !loading ? 'pointer' : 'not-allowed',
                opacity: isFormValid && !loading ? 1 : 0.5,
              }}
            >
              {loading ? (
                <>
                  <svg className="animate-spin h-5 w-5 text-white" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z" />
                  </svg>
                  AI is planning your trip…
                </>
              ) : (
                <>
                  <Sparkles size={18} />
                  Generate AI Plan
                  <ArrowRight size={16} />
                </>
              )}
            </motion.button>
          </motion.form>

          {/* ── Error ── */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 10 }}
                className="flex items-start gap-3 p-4 rounded-xl mb-8 text-sm"
                style={{ background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.25)' }}
              >
                <AlertCircle size={18} className="text-red-400 flex-shrink-0 mt-0.5" />
                <p className="text-red-300">{error}</p>
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Loading skeleton ── */}
          <AnimatePresence>
            {loading && (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="rounded-2xl p-8 space-y-4"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}
              >
                <div className="flex items-center gap-3 mb-6">
                  <div className="w-8 h-8 rounded-full flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg, #10b981, #0ea5e9)' }}>
                    <Sparkles size={14} className="text-white animate-pulse" />
                  </div>
                  <div>
                    <p className="text-white font-semibold text-sm">TripWise AI is crafting your itinerary</p>
                    <p className="text-white/40 text-xs">This usually takes 10–20 seconds…</p>
                  </div>
                </div>
                {[80, 60, 90, 50, 70, 40].map((w, i) => (
                  <div
                    key={i}
                    className="h-3 rounded-full animate-pulse"
                    style={{ width: `${w}%`, background: 'rgba(255,255,255,0.07)', animationDelay: `${i * 0.1}s` }}
                  />
                ))}
              </motion.div>
            )}
          </AnimatePresence>

          {/* ── Itinerary result ── */}
          <AnimatePresence>
            {itinerary && !loading && (
              <motion.div
                initial={{ opacity: 0, y: 24 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0 }}
                transition={{ duration: 0.5 }}
              >
                {/* Result header */}
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-2">
                    <div className="w-7 h-7 rounded-lg flex items-center justify-center"
                      style={{ background: 'linear-gradient(135deg, #10b981, #0ea5e9)' }}>
                      <Sparkles size={13} className="text-white" />
                    </div>
                    <span className="text-white font-semibold">Your AI Itinerary</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <button
                      onClick={() => setShowRouteMap(true)}
                      className="flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium text-white/70 hover:text-white transition-colors"
                      style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}>
                      <Map size={13} className="text-emerald-400" /> View Route Map
                    </button>
                    <span className="text-xs text-white/40 px-3 py-1 rounded-full"
                      style={{ background: 'rgba(255,255,255,0.05)' }}>
                      {form.destination} · {form.days} days · {form.travelers} traveler{parseInt(form.travelers) > 1 ? 's' : ''}
                    </span>
                  </div>
                </div>

                {/* Itinerary card */}
                <div
                  className="rounded-2xl p-6 sm:p-8 max-h-[75vh] overflow-y-auto scroll-smooth"
                  style={{
                    background: 'rgba(255,255,255,0.03)',
                    border: '1px solid rgba(255,255,255,0.08)',
                    scrollbarWidth: 'thin',
                    scrollbarColor: 'rgba(16,185,129,0.3) transparent',
                  }}
                >
                  {renderMarkdown(itinerary)}
                </div>

                {/* Re-plan button */}
                <button
                  onClick={() => { setItinerary(null); setShowRouteMap(false); window.scrollTo({ top: 0, behavior: 'smooth' }); }}
                  className="mt-4 text-sm text-white/40 hover:text-white/70 transition-colors flex items-center gap-1 mx-auto"
                >
                  ↑ Plan another trip
                </button>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Route Map Modal */}
          <RouteMapModal
            isOpen={showRouteMap}
            onClose={() => setShowRouteMap(false)}
            source={form.source}
            destination={form.destination}
            days={parseInt(form.days) || undefined}
            travelers={parseInt(form.travelers) || undefined}
            budget={parseFloat(form.budget) || undefined}
          />

        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Results;
