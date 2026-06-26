import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
  Plane, MapPin, Calendar, DollarSign, TrendingUp,
  Plus, Trash2, Eye, Sparkles, BarChart2, Globe, Map,
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import MapModal from '../components/MapModal';
import { getCityCoordsWithFallback } from '../utils/cityCoords';
import { useAuth } from '../context/AuthContext';
import { getTrips, deleteTrip, getAnalytics, type Trip, type AnalyticsDashboard } from '../services/api';

const statusColors: Record<string, string> = {
  planned:   'bg-sky-500/20 text-sky-400',
  completed: 'bg-emerald-500/20 text-emerald-400',
  cancelled: 'bg-red-500/20 text-red-400',
  draft:     'bg-white/10 text-white/60',
};

const Dashboard = () => {
  const [darkMode, setDarkMode]       = useState(true);
  const [trips, setTrips]             = useState<Trip[]>([]);
  const [analytics, setAnalytics]     = useState<AnalyticsDashboard | null>(null);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState('');
  const [deletingId, setDeletingId]   = useState<string | null>(null);
  const [showMap,    setShowMap]       = useState(false);

  const { user } = useAuth();
  const navigate  = useNavigate();

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      const [tripsRes, analyticsRes] = await Promise.all([
        getTrips(),
        getAnalytics(),
      ]);
      setTrips(tripsRes.trips || (tripsRes as unknown as Trip[]));
      setAnalytics(analyticsRes);
    } catch (e) {
      setError('Failed to load data. Make sure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this trip?')) return;
    setDeletingId(id);
    try {
      await deleteTrip(id);
      setTrips(prev => prev.filter(t => t.id !== id));
    } catch {
      alert('Delete failed. Try again.');
    } finally {
      setDeletingId(null);
    }
  };

  const displayName = user?.displayName || user?.email?.split('@')[0] || 'Traveller';
  const avatarUrl   = user?.photoURL || null;

  return (
    <div className="min-h-screen flex flex-col bg-[#020817] text-white">
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

      <main className="flex-grow pt-28 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">

        {/* ── Header ── */}
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-10 gap-4">
          <div className="flex items-center gap-4">
            {avatarUrl
              ? <img src={avatarUrl} alt="avatar" className="w-12 h-12 rounded-full border-2 border-emerald-500/40 object-cover" />
              : <div className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
                  style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                  {displayName[0].toUpperCase()}
                </div>
            }
            <div>
              <h1 className="text-2xl font-playfair font-bold">Welcome, {displayName} ✈️</h1>
              <p className="text-white/50 text-sm">Here's your travel overview</p>
            </div>
          </div>
          <Link to="/results">
            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }}
              className="flex items-center gap-2 px-5 py-2.5 rounded-xl font-medium text-sm text-white"
              style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
              <Plus size={16} /> Plan New Trip
            </motion.button>
          </Link>
          {trips.length > 0 && (
            <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.97 }}
              onClick={() => setShowMap(true)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm text-white/80 hover:text-white transition-colors"
              style={{ background: 'rgba(255,255,255,0.06)', border: '1px solid rgba(255,255,255,0.1)' }}>
              <Map size={16} className="text-emerald-400" /> Show Map
            </motion.button>
          )}
        </motion.div>

        {error && (
          <div className="p-4 rounded-xl mb-8 text-sm text-amber-300"
            style={{ background: 'rgba(245,158,11,0.1)', border: '1px solid rgba(245,158,11,0.25)' }}>
            ⚠️ {error}
          </div>
        )}

        {/* ── Analytics cards ── */}
        {analytics && (
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-4 mb-10">
            {[
              { label: 'Total Trips',    value: analytics.total_trips,     icon: Plane,     color: 'text-white' },
              { label: 'Planned',        value: analytics.planned_trips,   icon: Calendar,  color: 'text-sky-400' },
              { label: 'Completed',      value: analytics.completed_trips, icon: TrendingUp,color: 'text-emerald-400' },
              { label: 'Days Travelled', value: analytics.total_days_travelled, icon: Globe, color: 'text-purple-400' },
              { label: 'Budget Spent',   value: `₹${(analytics.total_budget_spent/1000).toFixed(0)}k`, icon: DollarSign, color: 'text-amber-400' },
              { label: 'Avg Cost',       value: `₹${(analytics.average_trip_cost/1000).toFixed(0)}k`,  icon: BarChart2,  color: 'text-pink-400' },
            ].map((s, i) => (
              <motion.div key={s.label} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 + i * 0.05 }}
                className="rounded-2xl p-4 flex flex-col gap-2"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>
                <s.icon size={18} className={s.color} />
                <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
                <div className="text-xs text-white/50">{s.label}</div>
              </motion.div>
            ))}
          </motion.div>
        )}

        {/* ── Favourite destination ── */}
        {analytics?.favorite_destination && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
            className="flex items-center gap-3 p-4 rounded-2xl mb-8"
            style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)' }}>
            <MapPin size={18} className="text-emerald-400 flex-shrink-0" />
            <p className="text-sm text-white/80">
              Your favourite destination: <span className="font-bold text-emerald-400">{analytics.favorite_destination}</span>
            </p>
          </motion.div>
        )}

        {/* ── Trips list ── */}
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-playfair font-bold">My Trips</h2>
          <span className="text-xs text-white/40">{trips.length} trip{trips.length !== 1 ? 's' : ''}</span>
        </div>

        {loading ? (
          <div className="space-y-4">
            {[1,2,3].map(i => (
              <div key={i} className="h-28 rounded-2xl animate-pulse"
                style={{ background: 'rgba(255,255,255,0.04)' }} />
            ))}
          </div>
        ) : trips.length === 0 ? (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            className="text-center py-20 rounded-2xl"
            style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
            <Sparkles size={36} className="text-emerald-400 mx-auto mb-4 opacity-50" />
            <p className="text-white/50 mb-4">No trips yet. Let's plan your first adventure!</p>
            <Link to="/results">
              <button className="px-6 py-2.5 rounded-xl text-white text-sm font-medium"
                style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                Plan a Trip
              </button>
            </Link>
          </motion.div>
        ) : (
          <div className="space-y-4">
            {trips.map((trip, i) => (
              <motion.div key={trip.id}
                initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.06 }}
                className="rounded-2xl p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 transition-all hover:border-white/20"
                style={{ background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.08)' }}>

                <div className="flex items-start gap-4 flex-1">
                  <div className="w-10 h-10 rounded-xl flex-shrink-0 flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                    <Plane size={18} className="text-white" />
                  </div>
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold">{trip.source_location} → {trip.destination_location}</h3>
                      <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium ${statusColors[trip.trip_status] || statusColors.draft}`}>
                        {trip.trip_status}
                      </span>
                    </div>
                    <div className="flex flex-wrap gap-4 text-xs text-white/50">
                      <span className="flex items-center gap-1"><Calendar size={11} /> {trip.number_of_days} days</span>
                      <span className="flex items-center gap-1"><DollarSign size={11} /> ₹{trip.budget.toLocaleString()}</span>
                      {trip.travel_mode && <span className="flex items-center gap-1"><Plane size={11} /> {trip.travel_mode}</span>}
                      <span>{new Date(trip.created_at).toLocaleDateString('en-IN', { day:'numeric', month:'short', year:'numeric' })}</span>
                      <span className="flex items-center gap-1 text-emerald-400 font-medium ml-2"><Sparkles size={11} /> Planned using AI</span>
                    </div>
                  </div>
                </div>

                <div className="flex items-center gap-2 self-end sm:self-auto">
                  <button onClick={() => navigate('/results')}
                    className="p-2 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-colors" title="View / Re-plan">
                    <Eye size={16} />
                  </button>
                  <button onClick={() => handleDelete(trip.id)} disabled={deletingId === trip.id}
                    className="p-2 rounded-lg text-red-400/60 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-40" title="Delete">
                    <Trash2 size={16} />
                  </button>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </main>

      {/* Map Modal — only mounts when user clicks Show Map */}
      <MapModal
        isOpen={showMap}
        onClose={() => setShowMap(false)}
        title="Your Trip Destinations"
        markers={trips
          .filter(t => t.destination_location)
          .map(t => {
            const [lat, lng] = getCityCoordsWithFallback(t.destination_location);
            return {
              lat, lng,
              title: t.destination_location,
              description: `${t.number_of_days} days · ₹${t.budget.toLocaleString()}`,
              category: t.trip_status,
            };
          })
        }
      />

      <Footer />
    </div>
  );
};

export default Dashboard;
