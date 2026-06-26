import { useState } from 'react';
import { motion } from 'framer-motion';
import { Link, useNavigate } from 'react-router-dom';
import {
  Settings, LogOut,
  ChevronRight, Plane, Star, BarChart2,
} from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { useAuth } from '../context/AuthContext';


const Profile = () => {
  const [darkMode,   setDarkMode]   = useState(true);
  const [activeTab,  setActiveTab]  = useState<'dashboard'|'settings'>('dashboard');
  const { user, logout }            = useAuth();
  const navigate                    = useNavigate();

  const displayName  = user?.displayName || user?.email?.split('@')[0] || 'Traveller';
  const displayEmail = user?.email || '';
  const avatarUrl    = user?.photoURL || null;

  const handleLogout = async () => {
    await logout();
    navigate('/');
  };

  const navItems = [
    { key: 'dashboard', icon: BarChart2, label: 'My Dashboard' },
    { key: 'settings',  icon: Settings,  label: 'Account Settings' },
  ] as const;

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-[#020817] text-white' : 'bg-gray-50 text-gray-900'}`}>
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

      <main className="flex-grow pt-28 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        <div className="flex flex-col lg:flex-row gap-8">

          {/* ── Sidebar ── */}
          <aside className="w-full lg:w-72 flex-shrink-0">
            <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
              className={`p-6 rounded-3xl border sticky top-28 ${darkMode ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200 shadow-sm'}`}>

              {/* Avatar */}
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
                <p className="text-sm text-white/60">{displayEmail}</p>
              </div>

              {/* Nav */}
              <nav className="pt-6 space-y-2">
                {navItems.map(item => (
                  <button key={item.key} onClick={() => setActiveTab(item.key)}
                    className={`w-full flex items-center justify-between p-3 rounded-xl transition-colors
                      ${activeTab === item.key
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : darkMode ? 'hover:bg-white/5 text-white/70' : 'hover:bg-gray-50 text-gray-700'}`}>
                    <div className="flex items-center gap-3">
                      <item.icon size={18} />
                      <span className="font-medium text-sm">{item.label}</span>
                    </div>
                    <ChevronRight size={16} className="opacity-50" />
                  </button>
                ))}

                <button onClick={handleLogout}
                  className={`w-full flex items-center gap-3 p-3 rounded-xl transition-colors mt-4 ${darkMode ? 'hover:bg-red-500/10 text-red-400' : 'hover:bg-red-50 text-red-600'}`}>
                  <LogOut size={18} />
                  <span className="font-medium text-sm">Log Out</span>
                </button>
              </nav>
            </motion.div>
          </aside>

          {/* ── Main content ── */}
          <div className="flex-1">

            {/* Dashboard tab — redirect to real dashboard */}
            {activeTab === 'dashboard' && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                className="text-center py-20 rounded-2xl"
                style={{ background: 'rgba(255,255,255,0.03)', border: '1px solid rgba(255,255,255,0.07)' }}>
                <Plane size={40} className="text-emerald-400 mx-auto mb-4 opacity-60" />
                <h2 className="text-2xl font-playfair font-bold mb-2">Your Trips Dashboard</h2>
                <p className="text-white/50 mb-6">See all your trips, analytics and planning in one place.</p>
                <Link to="/dashboard">
                  <button className="px-6 py-3 rounded-xl text-white font-medium"
                    style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                    Go to Dashboard →
                  </button>
                </Link>
              </motion.div>
            )}


            {/* Settings tab */}
            {activeTab === 'settings' && (
              <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
                <h2 className="text-2xl font-playfair font-bold mb-8">Account Settings</h2>
                <div className={`p-6 rounded-2xl border ${darkMode ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200 shadow-sm'}`}>
                  <h3 className="font-semibold mb-4 border-b border-white/10 pb-2">Personal Information</h3>
                  <form className="space-y-4 max-w-md" onSubmit={e => e.preventDefault()}>
                    <div>
                      <label className="block text-sm font-medium mb-1 opacity-80">Full Name</label>
                      <input type="text" defaultValue={displayName}
                        className={`w-full rounded-xl px-4 py-2 border focus:outline-none focus:ring-2 focus:ring-emerald-500/50 ${darkMode ? 'bg-white/5 border-white/10 text-white' : 'bg-gray-50 border-gray-200'}`} />
                    </div>
                    <div>
                      <label className="block text-sm font-medium mb-1 opacity-80">Email Address</label>
                      <input type="email" defaultValue={displayEmail} readOnly
                        className={`w-full rounded-xl px-4 py-2 border cursor-not-allowed opacity-60 ${darkMode ? 'bg-white/5 border-white/10 text-white' : 'bg-gray-50 border-gray-200'}`} />
                      <p className="text-xs text-white/40 mt-1">Email is managed by your sign-in provider</p>
                    </div>
                    <button type="submit" className="mt-4 px-6 py-2 rounded-xl bg-emerald-500 hover:bg-emerald-600 text-white text-sm font-medium transition-colors">
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
