import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
  Plane, MapPin, Calendar, DollarSign, TrendingUp,
  Plus, Trash2, Eye, Sparkles, BarChart2, Globe, Map,
  BookOpen, PenLine, X,
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import MapModal from '../components/MapModal';
import { getCityCoordsWithFallback } from '../utils/cityCoords';
import { useAuth } from '../context/AuthContext';
import { getTrips, deleteTrip, getAnalytics, type Trip, type AnalyticsDashboard } from '../services/api';

type Tab = 'trips' | 'analytics' | 'blog' | 'map';

interface BlogPost {
  id: string;
  title: string;
  destination: string;
  content: string;
  author: string;
  date: string;
}

const BLOG_KEY = 'tripwise_blogs';

const statusColors: Record<string, string> = {
  planned:   'bg-sky-500/20 text-sky-400',
  completed: 'bg-emerald-500/20 text-emerald-400',
  cancelled: 'bg-red-500/20 text-red-400',
  draft:     'bg-white/10 text-white/60',
};

const TABS = [
  { key: 'trips',     icon: Plane,    label: 'My Trips' },
  { key: 'analytics', icon: BarChart2, label: 'Analytics' },
  { key: 'blog',      icon: BookOpen, label: 'Travel Blog' },
  { key: 'map',       icon: Map,      label: 'Map' },
] as const;

const Dashboard = () => {
  const [activeTab,    setActiveTab]    = useState<Tab>('trips');
  const [trips,        setTrips]        = useState<Trip[]>([]);
  const [analytics,    setAnalytics]    = useState<AnalyticsDashboard | null>(null);
  const [loading,      setLoading]      = useState(true);
  const [error,        setError]        = useState('');
  const [deletingId,   setDeletingId]   = useState<string | null>(null);
  const [showMap,      setShowMap]      = useState(false);
  const [blogPosts,    setBlogPosts]    = useState<BlogPost[]>([]);
  const [showBlogForm, setShowBlogForm] = useState(false);
  const [blogForm,     setBlogForm]     = useState({ title: '', destination: '', content: '' });

  const { user } = useAuth();
  const navigate  = useNavigate();

  useEffect(() => { loadData(); loadBlogs(); }, []);

  const loadData = async () => {
    setLoading(true); setError('');
    try {
      const [tripsRes, analyticsRes] = await Promise.all([getTrips(), getAnalytics()]);
      setTrips(tripsRes.trips || (tripsRes as unknown as Trip[]));
      setAnalytics(analyticsRes);
    } catch { setError('Failed to load data. Backend may be starting up — try refreshing.'); }
    finally { setLoading(false); }
  };

  const loadBlogs = () => {
    try {
      const raw = localStorage.getItem(BLOG_KEY);
      setBlogPosts(raw ? JSON.parse(raw) : []);
    } catch { setBlogPosts([]); }
  };

  const saveBlog = () => {
    if (!blogForm.title.trim() || !blogForm.content.trim()) return;
    const post: BlogPost = {
      id: Date.now().toString(),
      title: blogForm.title.trim(),
      destination: blogForm.destination.trim() || 'India',
      content: blogForm.content.trim(),
      author: user?.displayName || user?.email?.split('@')[0] || 'Traveller',
      date: new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'short', year: 'numeric' }),
    };
    const updated = [post, ...blogPosts];
    setBlogPosts(updated);
    localStorage.setItem(BLOG_KEY, JSON.stringify(updated));
    setBlogForm({ title: '', destination: '', content: '' });
    setShowBlogForm(false);
  };

  const deleteBlog = (id: string) => {
    const updated = blogPosts.filter(p => p.id !== id);
    setBlogPosts(updated);
    localStorage.setItem(BLOG_KEY, JSON.stringify(updated));
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this trip?')) return;
    setDeletingId(id);
    try { await deleteTrip(id); setTrips(prev => prev.filter(t => t.id !== id)); }
    catch { alert('Delete failed. Try again.'); }
    finally { setDeletingId(null); }
  };

  const displayName = user?.displayName || user?.email?.split('@')[0] || 'Traveller';
  const avatarUrl   = user?.photoURL || null;

  return (
    <div className="min-h-screen flex flex-col bg-[#020817] text-white">
      <Navbar />

      <main className="flex-grow pt-24 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">

        {/* ── Header ── */}
        <motion.div initial={{ opacity:0, y:-20 }} animate={{ opacity:1, y:0 }}
          className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-8 gap-4">
          <div className="flex items-center gap-3">
            {avatarUrl
              ? <img src={avatarUrl} alt="avatar" className="w-11 h-11 rounded-full border-2 border-emerald-500/40 object-cover" />
              : <div className="w-11 h-11 rounded-full flex items-center justify-center text-white font-bold text-lg flex-shrink-0"
                  style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                  {displayName[0].toUpperCase()}
                </div>
            }
            <div>
              <h1 className="text-xl sm:text-2xl font-playfair font-bold">Welcome, {displayName} ✈️</h1>
              <p className="text-white/50 text-xs sm:text-sm">Your travel command centre</p>
            </div>
          </div>
          <Link to="/results">
            <motion.button whileHover={{ scale:1.05 }} whileTap={{ scale:0.97 }}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl font-medium text-sm text-white whitespace-nowrap"
              style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
              <Plus size={15} /> Plan New Trip
            </motion.button>
          </Link>
        </motion.div>

        {error && (
          <div className="p-4 rounded-xl mb-6 text-sm text-amber-300"
            style={{ background:'rgba(245,158,11,0.1)', border:'1px solid rgba(245,158,11,0.25)' }}>
            ⚠️ {error}
          </div>
        )}

        {/* ── Tab bar ── */}
        <div className="flex gap-2 mb-8 overflow-x-auto pb-1" style={{ scrollbarWidth:'none' }}>
          {TABS.map(tab => (
            <button key={tab.key} onClick={() => setActiveTab(tab.key as Tab)}
              className="flex items-center gap-2 px-4 py-2.5 rounded-xl text-sm font-medium whitespace-nowrap transition-all flex-shrink-0"
              style={activeTab === tab.key
                ? { background:'linear-gradient(135deg,#10b981,#0ea5e9)', color:'white' }
                : { background:'rgba(255,255,255,0.05)', color:'rgba(255,255,255,0.55)' }}>
              <tab.icon size={14} />{tab.label}
            </button>
          ))}
        </div>

        {/* ── TRIPS TAB ── */}
        {activeTab === 'trips' && (
          <motion.div key="trips" initial={{ opacity:0, y:10 }} animate={{ opacity:1, y:0 }}>
            <div className="flex items-center justify-between mb-5">
              <h2 className="text-lg font-playfair font-bold">My Trips</h2>
              <span className="text-xs text-white/40">{trips.length} trip{trips.length !== 1 ? 's' : ''}</span>
            </div>
            {loading ? (
              <div className="space-y-4">
                {[1,2,3].map(i => <div key={i} className="h-24 rounded-2xl animate-pulse" style={{ background:'rgba(255,255,255,0.04)' }} />)}
              </div>
            ) : trips.length === 0 ? (
              <div className="text-center py-20 rounded-2xl" style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.07)' }}>
                <Sparkles size={36} className="text-emerald-400 mx-auto mb-4 opacity-50" />
                <p className="text-white/50 mb-4">No trips yet. Let's plan your first adventure!</p>
                <Link to="/results">
                  <button className="px-6 py-2.5 rounded-xl text-white text-sm font-medium"
                    style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                    Plan a Trip
                  </button>
                </Link>
              </div>
            ) : (
              <div className="space-y-3">
                {trips.map((trip, i) => (
                  <motion.div key={trip.id} initial={{ opacity:0, y:16 }} animate={{ opacity:1, y:0 }} transition={{ delay:i*0.05 }}
                    className="rounded-2xl p-4 sm:p-5 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-3 transition-all hover:border-white/20"
                    style={{ background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.08)' }}>
                    <div className="flex items-start gap-3 flex-1 min-w-0">
                      <div className="w-9 h-9 rounded-xl flex-shrink-0 flex items-center justify-center" style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                        <Plane size={16} className="text-white" />
                      </div>
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2 mb-1">
                          <h3 className="font-semibold text-sm truncate">{trip.source_location} → {trip.destination_location}</h3>
                          <span className={`text-[10px] px-2 py-0.5 rounded-full font-medium flex-shrink-0 ${statusColors[trip.trip_status] || statusColors.draft}`}>
                            {trip.trip_status}
                          </span>
                        </div>
                        <div className="flex flex-wrap gap-3 text-xs text-white/50">
                          <span className="flex items-center gap-1"><Calendar size={10} />{trip.number_of_days}d</span>
                          <span className="flex items-center gap-1"><DollarSign size={10} />₹{trip.budget.toLocaleString()}</span>
                          <span>{new Date(trip.created_at).toLocaleDateString('en-IN',{day:'numeric',month:'short'})}</span>
                          <span className="flex items-center gap-1 text-emerald-400"><Sparkles size={10} />AI</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center gap-2 self-end sm:self-auto flex-shrink-0">
                      <button onClick={() => navigate('/results')} className="p-2 rounded-lg text-white/50 hover:text-white hover:bg-white/10 transition-colors" title="Re-plan"><Eye size={15} /></button>
                      <button onClick={() => handleDelete(trip.id)} disabled={deletingId === trip.id} className="p-2 rounded-lg text-red-400/60 hover:text-red-400 hover:bg-red-500/10 transition-colors disabled:opacity-40"><Trash2 size={15} /></button>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* ── ANALYTICS TAB ── */}
        {activeTab === 'analytics' && (
          <motion.div key="analytics" initial={{ opacity:0, y:10 }} animate={{ opacity:1, y:0 }}>
            <h2 className="text-lg font-playfair font-bold mb-6">Travel Analytics</h2>
            {loading ? (
              <div className="grid grid-cols-2 sm:grid-cols-3 gap-4">
                {[1,2,3,4,5,6].map(i => <div key={i} className="h-24 rounded-2xl animate-pulse" style={{ background:'rgba(255,255,255,0.04)' }} />)}
              </div>
            ) : !analytics ? (
              <div className="text-center py-16 text-white/40">No analytics data yet. Plan some trips first!</div>
            ) : (
              <>
                <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3 mb-8">
                  {[
                    { label:'Total Trips',    value: analytics.total_trips,                                          icon: Plane,      color:'text-white' },
                    { label:'Planned',        value: analytics.planned_trips,                                        icon: Calendar,   color:'text-sky-400' },
                    { label:'Completed',      value: analytics.completed_trips,                                      icon: TrendingUp, color:'text-emerald-400' },
                    { label:'Days Travelled', value: analytics.total_days_travelled,                                 icon: Globe,      color:'text-purple-400' },
                    { label:'Budget Spent',   value:`₹${(analytics.total_budget_spent/1000).toFixed(0)}k`,          icon: DollarSign, color:'text-amber-400' },
                    { label:'Avg Cost',       value:`₹${(analytics.average_trip_cost/1000).toFixed(0)}k`,           icon: BarChart2,  color:'text-pink-400' },
                  ].map((s,i) => (
                    <motion.div key={s.label} initial={{ opacity:0, y:10 }} animate={{ opacity:1, y:0 }} transition={{ delay:i*0.05 }}
                      className="rounded-2xl p-4 flex flex-col gap-2"
                      style={{ background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.08)' }}>
                      <s.icon size={16} className={s.color} />
                      <div className={`text-xl font-bold ${s.color}`}>{s.value}</div>
                      <div className="text-[10px] text-white/50 leading-tight">{s.label}</div>
                    </motion.div>
                  ))}
                </div>
                {analytics.favorite_destination && (
                  <div className="flex items-center gap-3 p-4 rounded-2xl mb-6"
                    style={{ background:'rgba(16,185,129,0.08)', border:'1px solid rgba(16,185,129,0.2)' }}>
                    <MapPin size={16} className="text-emerald-400 flex-shrink-0" />
                    <p className="text-sm text-white/80">
                      Favourite destination: <span className="font-bold text-emerald-400">{analytics.favorite_destination}</span>
                    </p>
                  </div>
                )}
                {analytics.top_destinations?.length > 0 && (
                  <div className="rounded-2xl p-5" style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.07)' }}>
                    <h3 className="font-semibold mb-4 text-sm text-white/70 uppercase tracking-wider">Top Destinations</h3>
                    <div className="space-y-3">
                      {analytics.top_destinations.slice(0,5).map((d,i) => (
                        <div key={d.destination} className="flex items-center gap-3">
                          <span className="text-xs text-white/40 w-4">{i+1}</span>
                          <div className="flex-1 h-2 rounded-full overflow-hidden" style={{ background:'rgba(255,255,255,0.08)' }}>
                            <div className="h-full rounded-full" style={{ background:'linear-gradient(90deg,#10b981,#0ea5e9)', width:`${Math.min(100,(d.count/analytics.total_trips)*100)}%` }} />
                          </div>
                          <span className="text-sm text-white/80 min-w-[80px]">{d.destination}</span>
                          <span className="text-xs text-white/40">{d.count}x</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </motion.div>
        )}

        {/* ── BLOG TAB ── */}
        {activeTab === 'blog' && (
          <motion.div key="blog" initial={{ opacity:0, y:10 }} animate={{ opacity:1, y:0 }}>
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-lg font-playfair font-bold">Travel Blog</h2>
              <button onClick={() => setShowBlogForm(v => !v)}
                className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-white transition-all"
                style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                {showBlogForm ? <X size={13} /> : <PenLine size={13} />}
                {showBlogForm ? 'Cancel' : 'Write Post'}
              </button>
            </div>

            <AnimatePresence>
              {showBlogForm && (
                <motion.div initial={{ opacity:0, y:-10 }} animate={{ opacity:1, y:0 }} exit={{ opacity:0, y:-10 }}
                  className="rounded-2xl p-5 mb-6"
                  style={{ background:'rgba(16,185,129,0.06)', border:'1px solid rgba(16,185,129,0.2)' }}>
                  <h3 className="font-semibold mb-4 text-sm">Share Your Experience ✍️</h3>
                  <div className="space-y-3">
                    <input type="text" placeholder="Post title (e.g. My Epic Goa Weekend)" value={blogForm.title}
                      onChange={e => setBlogForm(p => ({ ...p, title: e.target.value }))}
                      className="w-full rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/30 outline-none focus:ring-2 focus:ring-emerald-500/30"
                      style={{ background:'rgba(255,255,255,0.06)', border:'1px solid rgba(255,255,255,0.1)' }} />
                    <input type="text" placeholder="Destination (e.g. Goa, Kerala, Manali)" value={blogForm.destination}
                      onChange={e => setBlogForm(p => ({ ...p, destination: e.target.value }))}
                      className="w-full rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/30 outline-none focus:ring-2 focus:ring-emerald-500/30"
                      style={{ background:'rgba(255,255,255,0.06)', border:'1px solid rgba(255,255,255,0.1)' }} />
                    <textarea placeholder="Share your travel story, tips, must-visit spots, food recommendations..." value={blogForm.content}
                      onChange={e => setBlogForm(p => ({ ...p, content: e.target.value }))}
                      rows={5} className="w-full rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-white/30 outline-none resize-none focus:ring-2 focus:ring-emerald-500/30"
                      style={{ background:'rgba(255,255,255,0.06)', border:'1px solid rgba(255,255,255,0.1)' }} />
                    <button onClick={saveBlog} disabled={!blogForm.title.trim() || !blogForm.content.trim()}
                      className="px-5 py-2 rounded-xl text-sm font-medium text-white disabled:opacity-40 transition-opacity"
                      style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                      Publish Post
                    </button>
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            {blogPosts.length === 0 ? (
              <div className="text-center py-20 rounded-2xl" style={{ background:'rgba(255,255,255,0.03)', border:'1px solid rgba(255,255,255,0.07)' }}>
                <BookOpen size={36} className="text-emerald-400 mx-auto mb-4 opacity-50" />
                <p className="text-white/50 mb-1">No blog posts yet</p>
                <p className="text-white/30 text-sm">Write about your travel experiences and inspire others!</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {blogPosts.map((post, i) => (
                  <motion.div key={post.id} initial={{ opacity:0, y:16 }} animate={{ opacity:1, y:0 }} transition={{ delay:i*0.05 }}
                    className="rounded-2xl p-5 flex flex-col gap-3 hover:border-white/20 transition-all"
                    style={{ background:'rgba(255,255,255,0.04)', border:'1px solid rgba(255,255,255,0.08)' }}>
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <h3 className="font-bold text-white text-base leading-tight mb-1 line-clamp-2">{post.title}</h3>
                        <div className="flex flex-wrap items-center gap-2 text-xs">
                          <span className="flex items-center gap-1 text-emerald-400 font-medium"><MapPin size={10} />{post.destination}</span>
                          <span className="text-white/40">{post.author}</span>
                          <span className="text-white/30">{post.date}</span>
                        </div>
                      </div>
                      <button onClick={() => deleteBlog(post.id)} className="text-red-400/50 hover:text-red-400 transition-colors flex-shrink-0 p-1">
                        <Trash2 size={14} />
                      </button>
                    </div>
                    <p className="text-white/65 text-sm leading-relaxed line-clamp-4">{post.content}</p>
                    <div className="pt-2 border-t border-white/5">
                      <span className="text-xs text-emerald-400/60 flex items-center gap-1"><Sparkles size={10} />TripWise Blog</span>
                    </div>
                  </motion.div>
                ))}
              </div>
            )}
          </motion.div>
        )}

        {/* ── MAP TAB ── */}
        {activeTab === 'map' && (
          <motion.div key="map" initial={{ opacity:0, y:10 }} animate={{ opacity:1, y:0 }} className="text-center py-20">
            <div className="w-16 h-16 rounded-2xl flex items-center justify-center mx-auto mb-5"
              style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
              <Map size={28} className="text-white" />
            </div>
            <h3 className="text-xl font-playfair font-bold mb-2">Trip Map</h3>
            <p className="text-white/50 mb-8 max-w-sm mx-auto">See all your travel destinations plotted on an interactive map</p>
            {trips.length === 0 ? (
              <div>
                <p className="text-white/30 mb-4">No trips yet to show on map</p>
                <Link to="/results"><button className="px-6 py-2.5 rounded-xl text-white text-sm font-medium" style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>Plan a Trip First</button></Link>
              </div>
            ) : (
              <button onClick={() => setShowMap(true)}
                className="px-8 py-3 rounded-xl text-white font-semibold"
                style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                Open Map ({trips.length} destination{trips.length !== 1 ? 's' : ''})
              </button>
            )}
          </motion.div>
        )}

      </main>

      <MapModal isOpen={showMap} onClose={() => setShowMap(false)} title="Your Trip Destinations"
        markers={trips.filter(t => t.destination_location).map(t => {
          const [lat, lng] = getCityCoordsWithFallback(t.destination_location);
          return { lat, lng, title: t.destination_location, description:`${t.number_of_days} days · ₹${t.budget.toLocaleString()}`, category: t.trip_status };
        })} />

      <Footer />
    </div>
  );
};

export default Dashboard;
