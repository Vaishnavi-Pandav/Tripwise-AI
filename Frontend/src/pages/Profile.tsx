import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';
import { User, MapPin, Calendar, Heart, Settings, LogOut, ChevronRight, Plane, Star } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const Profile = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState('trips');
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const displayName = user?.displayName || user?.email?.split('@')[0] || 'Traveller';
  const displayEmail = user?.email || '';
  const avatarUrl = user?.photoURL || null;

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

const SAVED_TRIPS = [
  {
    id: 't1',
    name: 'Summer in Kyoto',
    destination: 'Kyoto, Japan',
    date: 'Jul 15 - Jul 25, 2026',
    image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=400&q=80',
    status: 'Upcoming'
  },
  {
    id: 't2',
    name: 'Alps Ski Retreat',
    destination: 'Zermatt, Switzerland',
    date: 'Jan 10 - Jan 18, 2026',
    image: 'https://images.unsplash.com/photo-1531366936337-7c912a458b1c?auto=format&fit=crop&w=400&q=80',
    status: 'Completed'
  }
];

const WISHLIST = [
  {
    id: 'w1',
    name: 'Amalfi Coast',
    country: 'Italy',
    image: 'https://images.unsplash.com/photo-1533676802871-eca1ae998cd5?auto=format&fit=crop&w=400&q=80',
  },
  {
    id: 'w2',
    name: 'Santorini',
    country: 'Greece',
    image: 'https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?auto=format&fit=crop&w=400&q=80',
  },
  {
    id: 'w3',
    name: 'Banff',
    country: 'Canada',
    image: 'https://images.unsplash.com/photo-1521404169724-699e190ebf9e?auto=format&fit=crop&w=400&q=80',
  }
];

const Profile = () => {
  const [darkMode, setDarkMode] = useState(true);
  const [activeTab, setActiveTab] = useState('trips'); // 'trips', 'wishlist', 'settings'

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-[#020817] text-white' : 'bg-gray-50 text-gray-900'}`}>
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
      
      <main className="flex-grow pt-28 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        
        <div className="flex flex-col lg:flex-row gap-8">
          
          {/* Left Sidebar - Profile Summary */}
          <aside className="w-full lg:w-80 flex-shrink-0">
            <motion.div 
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              className={`p-6 rounded-3xl border sticky top-28 ${darkMode ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200 shadow-sm'}`}
            >
              {/* Avatar & Info */}
              <div className="flex flex-col items-center text-center pb-6 border-b border-white/10">
                <div className="relative mb-4">
                  {avatarUrl
                    ? <img src={avatarUrl} alt={displayName} className="w-24 h-24 rounded-full object-cover border-4 border-emerald-500/30" />
                    : <div className="w-24 h-24 rounded-full flex items-center justify-center text-white font-bold text-3xl border-4 border-emerald-500/30"
                        style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                        {displayName[0].toUpperCase()}
                      </div>
                  }
                  <div className="absolute bottom-0 right-0 bg-emerald-500 text-white w-7 h-7 rounded-full flex items-center justify-center border-2 border-[#020817]">
                    <Star size={12} className="fill-white" />
                  </div>
                </div>
                <h1 className="text-xl font-bold font-playfair mb-1">{displayName}</h1>
                <p className={`text-sm mb-2 ${darkMode ? 'text-white/60' : 'text-gray-500'}`}>{displayEmail}</p>
              </div>

              {/* Quick Stats */}
              <div className="grid grid-cols-3 gap-2 py-6 border-b border-white/10">
                <div className="text-center">
                  <div className="text-xl font-bold text-emerald-400">{MOCK_USER.stats.trips}</div>
                  <div className={`text-xs mt-1 ${darkMode ? 'text-white/50' : 'text-gray-500'}`}>Trips</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-sky-400">{MOCK_USER.stats.countries}</div>
                  <div className={`text-xs mt-1 ${darkMode ? 'text-white/50' : 'text-gray-500'}`}>Countries</div>
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-amber-400">{MOCK_USER.stats.saved}</div>
                  <div className={`text-xs mt-1 ${darkMode ? 'text-white/50' : 'text-gray-500'}`}>Saved</div>
                </div>
              </div>

              {/* Navigation */}
              <nav className="pt-6 space-y-2">
                <button 
                  onClick={() => setActiveTab('trips')}
                  className={`w-full flex items-center justify-between p-3 rounded-xl transition-colors ${activeTab === 'trips' ? (darkMode ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-50 text-emerald-600') : (darkMode ? 'hover:bg-white/5 text-white/70' : 'hover:bg-gray-50 text-gray-700')}`}
                >
                  <div className="flex items-center gap-3">
                    <Plane size={18} /> <span className="font-medium text-sm">My Trips</span>
                  </div>
                  <ChevronRight size={16} className="opacity-50" />
                </button>
                <button 
                  onClick={() => setActiveTab('wishlist')}
                  className={`w-full flex items-center justify-between p-3 rounded-xl transition-colors ${activeTab === 'wishlist' ? (darkMode ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-50 text-emerald-600') : (darkMode ? 'hover:bg-white/5 text-white/70' : 'hover:bg-gray-50 text-gray-700')}`}
                >
                  <div className="flex items-center gap-3">
                    <Heart size={18} /> <span className="font-medium text-sm">Wishlist</span>
                  </div>
                  <ChevronRight size={16} className="opacity-50" />
                </button>
                <button 
                  onClick={() => setActiveTab('settings')}
                  className={`w-full flex items-center justify-between p-3 rounded-xl transition-colors ${activeTab === 'settings' ? (darkMode ? 'bg-emerald-500/20 text-emerald-400' : 'bg-emerald-50 text-emerald-600') : (darkMode ? 'hover:bg-white/5 text-white/70' : 'hover:bg-gray-50 text-gray-700')}`}
                >
                  <div className="flex items-center gap-3">
                    <Settings size={18} /> <span className="font-medium text-sm">Account Settings</span>
                  </div>
                  <ChevronRight size={16} className="opacity-50" />
                </button>
                
                <Link to="/login" onClick={handleLogout} className={`w-full flex items-center justify-between p-3 rounded-xl transition-colors mt-4 ${darkMode ? 'hover:bg-red-500/10 text-red-400' : 'hover:bg-red-50 text-red-600'}`}>
                  <div className="flex items-center gap-3">
                    <LogOut size={18} /> <span className="font-medium text-sm">Log Out</span>
                  </div>
                </Link>
              </nav>
            </motion.div>
          </aside>

          {/* Right Content Area */}
          <div className="flex-1">
            
            {/* Trips Tab */}
            {activeTab === 'trips' && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <div className="flex justify-between items-center mb-8">
                  <h2 className="text-2xl font-playfair font-bold">My Trips</h2>
                  <Link to="/results" className="px-4 py-2 rounded-full bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors shadow-lg shadow-emerald-500/20">
                    Plan New Trip
                  </Link>
                </div>

                <div className="space-y-6">
                  {SAVED_TRIPS.map(trip => (
                    <div 
                      key={trip.id} 
                      className={`p-4 rounded-2xl border flex flex-col sm:flex-row gap-5 transition-all hover:shadow-lg ${darkMode ? 'bg-white/5 border-white/10 hover:border-white/20' : 'bg-white border-gray-200 shadow-sm'}`}
                    >
                      <img 
                        src={trip.image} 
                        alt={trip.name} 
                        className="w-full sm:w-48 h-32 object-cover rounded-xl"
                      />
                      <div className="flex-1 flex flex-col justify-center">
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <span className={`inline-block px-2.5 py-1 rounded-md text-[10px] font-bold uppercase tracking-wider mb-2 ${trip.status === 'Upcoming' ? 'bg-sky-500/20 text-sky-400' : 'bg-emerald-500/20 text-emerald-400'}`}>
                              {trip.status}
                            </span>
                            <h3 className="text-lg font-bold font-playfair leading-tight">{trip.name}</h3>
                          </div>
                          <button className={`p-2 rounded-lg ${darkMode ? 'bg-white/5 hover:bg-white/10' : 'bg-gray-100 hover:bg-gray-200'}`}>
                            <ChevronRight size={16} />
                          </button>
                        </div>
                        <div className="space-y-1.5 mt-2">
                          <div className={`flex items-center gap-2 text-sm ${darkMode ? 'text-white/60' : 'text-gray-500'}`}>
                            <MapPin size={14} className="text-emerald-400" /> {trip.destination}
                          </div>
                          <div className={`flex items-center gap-2 text-sm ${darkMode ? 'text-white/60' : 'text-gray-500'}`}>
                            <Calendar size={14} className="text-blue-400" /> {trip.date}
                          </div>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Wishlist Tab */}
            {activeTab === 'wishlist' && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <h2 className="text-2xl font-playfair font-bold mb-8">Saved Destinations</h2>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
                  {WISHLIST.map(item => (
                    <div 
                      key={item.id} 
                      className={`group rounded-2xl overflow-hidden border transition-all hover:-translate-y-1 ${darkMode ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200 shadow-sm'}`}
                    >
                      <div className="relative h-40 overflow-hidden">
                        <img 
                          src={item.image} 
                          alt={item.name} 
                          className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
                        />
                        <button className="absolute top-3 right-3 p-2 bg-black/40 backdrop-blur-md rounded-full text-white hover:bg-red-500/80 transition-colors">
                          <Heart size={14} className="fill-white" />
                        </button>
                      </div>
                      <div className="p-4">
                        <h3 className="font-bold text-lg">{item.name}</h3>
                        <div className={`flex items-center gap-1.5 text-sm mt-1 ${darkMode ? 'text-white/60' : 'text-gray-500'}`}>
                          <MapPin size={12} className="text-emerald-400" /> {item.country}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}

            {/* Settings Tab (Placeholder) */}
            {activeTab === 'settings' && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <h2 className="text-2xl font-playfair font-bold mb-8">Account Settings</h2>
                
                <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200 shadow-sm'}`}>
                  <h3 className="font-semibold mb-4 border-b border-white/10 pb-2">Personal Information</h3>
                  <form className="space-y-4 max-w-md">
                    <div>
                      <label className="block text-sm font-medium mb-1 opacity-80">Full Name</label>
                      <input type="text" defaultValue={MOCK_USER.name} className={`w-full rounded-xl px-4 py-2 border focus:outline-none focus:ring-2 focus:ring-emerald-500/50 ${darkMode ? 'bg-white/5 border-white/10 text-white' : 'bg-gray-50 border-gray-200'}`} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 opacity-80">Email Address</label>
                      <input type="email" defaultValue={MOCK_USER.email} className={`w-full rounded-xl px-4 py-2 border focus:outline-none focus:ring-2 focus:ring-emerald-500/50 ${darkMode ? 'bg-white/5 border-white/10 text-white' : 'bg-gray-50 border-gray-200'}`} />
                    </div>
                    <button type="button" className="mt-4 px-6 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors">
                      Save Changes
                    </button>
                  </form>
                </div>
              </motion.div>
            )}

          </div>
        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Profile;
