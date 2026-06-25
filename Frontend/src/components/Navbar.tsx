import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Menu, X, Plane, User, Heart, Settings, LogOut, History, MapPin, ChevronDown, Building2 } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LoginModal from "./LoginModal";

// Dark mode removed — app is always dark
interface NavbarProps {
  darkMode?: boolean;
  setDarkMode?: (v: boolean) => void;
}

const navLinks = [
  { label: "Home",         href: "/#home" },
  { label: "Destinations", href: "/#destinations" },
  { label: "AI Planner",   href: "/#ai-planner" },
  { label: "Packages",     href: "/#packages" },
  { label: "Agencies",     href: "/agencies", isRoute: true },
  { label: "Reviews",      href: "/#reviews" },
];

const Navbar = ({ }: NavbarProps) => {
  const [scrolled,     setScrolled]     = useState(false);
  const [menuOpen,     setMenuOpen]     = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);

  const [showLogin,    setShowLogin]    = useState(false);

  const { user, logout } = useAuth();
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate    = useNavigate();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    const handleOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node))
        setDropdownOpen(false);
    };
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  const scrollTo = (href: string, isRoute?: boolean) => {
    setMenuOpen(false);
    if (isRoute || !href.startsWith("/#")) {
      navigate(href);
    } else {
      if (window.location.pathname !== "/") navigate(href);
      else document.querySelector(href.replace("/#","#"))?.scrollIntoView({ behavior:"smooth", block:"start" });
    }
  };

  // "Plan My Trip" → opens chat if logged in, else login modal
  const handlePlanMyTrip = () => {
    setMenuOpen(false);
    if (user) navigate("/chat");
    else setShowLogin(true);
  };

  const handleLogout = async () => {
    setDropdownOpen(false); setMenuOpen(false);
    await logout(); navigate("/");
  };

  const avatarUrl   = user?.photoURL || null;
  const displayName = user?.displayName || user?.email?.split("@")[0] || "User";
  const displayEmail= user?.email || "";

  // ── Always dark — hardcoded colors ──────────────────────────────────────────
  const textColor      = "text-white";
  const textMuted      = "text-white/70";
  const bgGlass        = "rgba(255,255,255,0.06)";
  const borderGlass    = "rgba(255,255,255,0.12)";
  const navBg          = scrolled ? "rgba(2,8,23,0.85)" : "transparent";
  const navBorder      = scrolled ? "1px solid rgba(255,255,255,0.08)" : "none";
  const dropdownBg     = "rgba(2,8,23,0.97)";
  const dropdownBorder = "rgba(255,255,255,0.15)";
  const dropdownItem   = "text-white/70 hover:text-white hover:bg-white/10";
  const mobileMenu     = "rgba(2,8,23,0.95)";

  return (
    <>
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="fixed top-0 left-0 right-0 z-50 transition-all duration-500"
        style={{
          background: scrolled
            ? darkMode ? "rgba(2,8,23,0.85)" : "rgba(255,255,255,0.92)"
            : "transparent",
          backdropFilter: scrolled ? "blur(20px)" : "none",
          borderBottom: navBorder,
        }}
      >
        <div className="container-custom">
          <div className="flex items-center justify-between h-20">

            {/* Logo */}
            <motion.div whileHover={{ scale: 1.03 }}
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => { navigate("/"); setTimeout(() => window.scrollTo({ top:0, behavior:"smooth" }),100); }}>
              <div className="relative">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ background:"linear-gradient(135deg,#10b981,#0ea5e9)" }}>
                  <Plane size={20} color="white" />
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
              </div>
              <div>
                <span className={`text-xl font-bold ${textColor}`}
                  style={{ fontFamily:"'Inter',sans-serif", letterSpacing:"-0.02em" }}>
                  TripWise<span className="gradient-text">AI</span>
                </span>
                <div className="text-xs text-emerald-500 font-medium" style={{ marginTop:"-2px", letterSpacing:"0.05em" }}>
                  TRAVEL SMARTER
                </div>
              </div>
            </motion.div>

            {/* Desktop Nav Links */}
            <div className="hidden lg:flex items-center gap-8">
              {navLinks.map(link => (
                <button key={link.href} onClick={() => scrollTo(link.href, link.isRoute)}
                  className={`nav-link bg-transparent border-none ${textMuted} hover:text-emerald-500 transition-colors font-medium text-sm`}>
                  {link.label === 'Agencies' && <Building2 size={13} className="inline mr-1 text-emerald-400" />}
                  {link.label}
                </button>
              ))}
            </div>

            {/* Right controls */}
            <div className="flex items-center gap-3">

              {/* Dark mode toggle removed — app is always dark */}



              {/* Desktop auth */}
              <div className="hidden lg:flex items-center gap-2">
                {!user ? (
                  <>
                    <motion.button whileHover={{ scale:1.05 }} whileTap={{ scale:0.95 }}
                      onClick={() => setShowLogin(true)}
                      className={`px-4 py-2 rounded-full text-sm font-medium ${textColor} transition-all`}
                      style={{ background: bgGlass, border:`1px solid ${borderGlass}` }}>
                      Log In
                    </motion.button>
                    <motion.button whileHover={{ scale:1.05 }} whileTap={{ scale:0.95 }}
                      onClick={() => setShowLogin(true)}
                      className="px-4 py-2 rounded-full text-sm font-medium text-white transition-all"
                      style={{ background:"linear-gradient(135deg,#10b981,#0ea5e9)" }}>
                      Sign Up
                    </motion.button>
                  </>
                ) : (
                  <div className="relative" ref={dropdownRef}>
                    <motion.button whileHover={{ scale:1.05 }} whileTap={{ scale:0.95 }}
                      onClick={() => setDropdownOpen(!dropdownOpen)}
                      className="flex items-center gap-2 p-1 pr-3 rounded-full border transition-all"
                      style={{ background: bgGlass, borderColor: borderGlass }}>
                      {avatarUrl
                        ? <img src={avatarUrl} alt="avatar" className="w-8 h-8 rounded-full object-cover border border-emerald-500/30" />
                        : <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm"
                            style={{ background:"linear-gradient(135deg,#10b981,#0ea5e9)" }}>
                            {displayName[0].toUpperCase()}
                          </div>
                      }
                      <ChevronDown size={14} className="text-white/70" />
                    </motion.button>

                    <AnimatePresence>
                      {dropdownOpen && (
                        <motion.div
                          initial={{ opacity:0, y:10, scale:0.95 }} animate={{ opacity:1, y:0, scale:1 }}
                          exit={{ opacity:0, y:10, scale:0.95 }} transition={{ duration:0.2 }}
                          className="absolute right-0 mt-3 w-60 rounded-2xl overflow-hidden shadow-2xl border"
                          style={{ background: dropdownBg, borderColor: dropdownBorder, backdropFilter:"blur(20px)" }}>
                          <div className="p-5 border-b border-white/10">
                            <p className={`text-sm font-bold mb-0.5 ${textColor}`}>{displayName}</p>
                            <p className={`text-xs ${textMuted}`}>{displayEmail}</p>
                          </div>
                          <div className="p-2 flex flex-col gap-1">
                            {[
                              { icon: User,    label:"My Profile",  to:"/profile" },
                              { icon: MapPin,  label:"Saved Trips", to:"/profile" },
                              { icon: History, label:"Trip History",to:"/profile" },
                              { icon: Heart,   label:"Wishlist",    to:"/profile" },
                              { icon: Settings,label:"Settings",    to:"/profile" },
                            ].map((item,i) => (
                              <Link key={i} to={item.to} onClick={() => setDropdownOpen(false)}
                                className={`flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-colors ${dropdownItem}`}>
                                <item.icon size={16} className="text-emerald-500" /> {item.label}
                              </Link>
                            ))}
                            <div className={`h-px my-2 mx-2 ${darkMode?"bg-white/10":"bg-gray-100"}`} />
                            <button onClick={handleLogout}
                              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-red-500 hover:bg-red-500/10 transition-colors text-left">
                              <LogOut size={16} /> Logout
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )}

                <motion.button whileHover={{ scale:1.05 }} whileTap={{ scale:0.95 }}
                  onClick={handlePlanMyTrip}
                  className="flex items-center gap-2 text-white ml-1"
                  style={{ background:"linear-gradient(135deg,#10b981,#0ea5e9)", padding:"10px 20px", borderRadius:"50px", fontSize:"14px", fontWeight:600, border:"none", cursor:"pointer" }}>
                  <span>AI Chat</span>
                  <Plane size={15} />
                </motion.button>
              </div>

              {/* Mobile hamburger */}
              <motion.button whileTap={{ scale:0.9 }} onClick={() => setMenuOpen(!menuOpen)}
                className="lg:hidden w-10 h-10 rounded-full flex items-center justify-center"
                style={{ background: bgGlass, border:`1px solid ${borderGlass}` }}
                aria-label="Toggle menu">
                {menuOpen ? <X size={18} className={textColor} /> : <Menu size={18} className={textColor} />}
              </motion.button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity:0, y:-20 }} animate={{ opacity:1, y:0 }}
            exit={{ opacity:0, y:-20 }} transition={{ duration:0.3 }}
            className="fixed inset-0 z-40 lg:hidden overflow-y-auto"
            style={{ top:"80px" }}>
            <div className="min-h-full p-6 flex flex-col gap-4 pb-20"
              style={{ background: mobileMenu, backdropFilter:"blur(20px)" }}>

              <div className={`flex flex-col gap-3 mb-6 pb-6 border-b ${darkMode?"border-white/10":"border-gray-200"}`}>
                {!user ? (
                  <>
                    <button onClick={() => { setMenuOpen(false); setShowLogin(true); }}
                      className={`w-full py-3 rounded-xl font-medium border transition-colors ${darkMode?"bg-white/5 border-white/10 text-white hover:bg-white/10":"bg-gray-50 border-gray-200 text-gray-900 hover:bg-gray-100"}`}>
                      Log In
                    </button>
                    <button onClick={() => { setMenuOpen(false); setShowLogin(true); }}
                      className="w-full py-3 rounded-xl text-white font-medium"
                      style={{ background:"linear-gradient(135deg,#10b981,#0ea5e9)" }}>
                      Sign Up
                    </button>
                  </>
                ) : (
                  <div className="flex flex-col gap-3">
                    <div className={`flex items-center gap-4 p-4 rounded-2xl border ${darkMode?"bg-white/5 border-white/10":"bg-gray-50 border-gray-200"}`}>
                      {avatarUrl
                        ? <img src={avatarUrl} alt="avatar" className="w-12 h-12 rounded-full object-cover border-2 border-emerald-500/50" />
                        : <div className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
                            style={{ background:"linear-gradient(135deg,#10b981,#0ea5e9)" }}>
                            {displayName[0].toUpperCase()}
                          </div>
                      }
                      <div>
                        <p className={`font-bold ${textColor}`}>{displayName}</p>
                        <p className="text-xs text-emerald-500">{displayEmail}</p>
                      </div>
                    </div>
                    <Link to="/chat" onClick={() => setMenuOpen(false)}>
                      <button className={`w-full flex items-center justify-center gap-2 py-3 rounded-xl font-medium border transition-colors ${darkMode?"bg-white/5 border-white/10 text-white":"bg-gray-50 border-gray-200 text-gray-900"}`}>
                        <MessageCircle size={16} className="text-emerald-500" /> AI Chat
                      </button>
                    </Link>
                    <button onClick={handleLogout}
                      className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-red-500/10 text-red-500 font-medium hover:bg-red-500/20 transition-colors">
                      <LogOut size={16} /> Logout
                    </button>
                  </div>
                )}
              </div>

              {navLinks.map((link,i) => (
                <motion.button key={link.href}
                  initial={{ opacity:0, x:-20 }} animate={{ opacity:1, x:0 }}
                  transition={{ delay: i * 0.07 }}
                  onClick={() => scrollTo(link.href, link.isRoute)}
                  className={`text-left text-lg font-medium py-3 px-4 rounded-xl transition-all bg-transparent border-none cursor-pointer ${darkMode?"text-white/80 hover:text-white hover:bg-white/5":"text-gray-700 hover:text-gray-900 hover:bg-gray-100"}`}>
                  {link.label}
                </motion.button>
              ))}

              <motion.button initial={{ opacity:0 }} animate={{ opacity:1 }} transition={{ delay:0.4 }}
                onClick={handlePlanMyTrip} className="btn-primary mt-4">
                AI Chat ✈️
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <LoginModal isOpen={showLogin} onClose={() => setShowLogin(false)} redirectTo="/results" />
    </>
  );
};

export default Navbar;
