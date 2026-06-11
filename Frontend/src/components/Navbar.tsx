import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Moon, Sun, Menu, X, Plane, User, Heart, Settings, LogOut, History, MapPin, ChevronDown } from "lucide-react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LoginModal from "./LoginModal";

interface NavbarProps {
  darkMode: boolean;
  setDarkMode: (v: boolean) => void;
}

const navLinks = [
  { label: "Home",         href: "/#home" },
  { label: "Destinations", href: "/#destinations" },
  { label: "AI Planner",   href: "/#ai-planner" },
  { label: "Packages",     href: "/#packages" },
  { label: "Reviews",      href: "/#reviews" },
  { label: "Contact",      href: "/#contact" },
];

const Navbar = ({ darkMode, setDarkMode }: NavbarProps) => {
  const [scrolled,     setScrolled]     = useState(false);
  const [menuOpen,     setMenuOpen]     = useState(false);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [showLogin,    setShowLogin]    = useState(false);

  const { user, logout } = useAuth();
  const dropdownRef = useRef<HTMLDivElement>(null);
  const navigate    = useNavigate();

  // ── Scroll listener ──────────────────────────────────────────────────────
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  // ── Close dropdown on outside click ─────────────────────────────────────
  useEffect(() => {
    const handleOutside = (e: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target as Node))
        setDropdownOpen(false);
    };
    document.addEventListener("mousedown", handleOutside);
    return () => document.removeEventListener("mousedown", handleOutside);
  }, []);

  // ── Navigation helper ────────────────────────────────────────────────────
  const scrollTo = (href: string) => {
    setMenuOpen(false);
    if (href.startsWith("/#")) {
      if (window.location.pathname !== "/") {
        navigate(href);
      } else {
        document.querySelector(href.replace("/#", "#"))
          ?.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    }
  };

  const handlePlanMyTrip = () => {
    setMenuOpen(false);
    if (user) navigate("/results");
    else setShowLogin(true);
  };

  const handleLogout = async () => {
    setDropdownOpen(false);
    setMenuOpen(false);
    await logout();
    navigate("/");
  };

  // ── Avatar helpers ───────────────────────────────────────────────────────
  const avatarUrl = user?.photoURL || null;
  const displayName = user?.displayName || user?.email?.split("@")[0] || "User";
  const displayEmail = user?.email || "";

  return (
    <>
      {/* ── Navbar ─────────────────────────────────────────────────────────── */}
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled ? "glass-dark shadow-2xl shadow-black/40" : "bg-transparent"
        }`}
        style={{ borderBottom: scrolled ? "1px solid rgba(255,255,255,0.08)" : "none" }}
      >
        <div className="container-custom">
          <div className="flex items-center justify-between h-20">

            {/* Logo */}
            <motion.div
              whileHover={{ scale: 1.03 }}
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => { navigate("/"); setTimeout(() => window.scrollTo({ top: 0, behavior: "smooth" }), 100); }}
            >
              <div className="relative">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ background: "linear-gradient(135deg, #10b981, #0ea5e9)" }}>
                  <Plane size={20} color="white" />
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
              </div>
              <div>
                <span className="text-xl font-bold text-white"
                  style={{ fontFamily: "'Inter', sans-serif", letterSpacing: "-0.02em" }}>
                  TripWise<span className="gradient-text">AI</span>
                </span>
                <div className="text-xs text-emerald-400 font-medium"
                  style={{ marginTop: "-2px", letterSpacing: "0.05em" }}>
                  TRAVEL SMARTER
                </div>
              </div>
            </motion.div>

            {/* Desktop Nav Links */}
            <div className="hidden lg:flex items-center gap-8">
              {navLinks.map(link => (
                <button key={link.href} onClick={() => scrollTo(link.href)}
                  className="nav-link bg-transparent border-none text-white hover:text-emerald-400 transition-colors font-medium text-sm">
                  {link.label}
                </button>
              ))}
            </div>

            {/* Right controls */}
            <div className="flex items-center gap-4">

              {/* Dark mode toggle */}
              <motion.button whileHover={{ scale: 1.1 }} whileTap={{ scale: 0.9 }}
                onClick={() => setDarkMode(!darkMode)}
                className="hidden sm:flex w-10 h-10 rounded-full items-center justify-center border transition-all"
                style={{ background: "rgba(255,255,255,0.06)", borderColor: "rgba(255,255,255,0.12)" }}
                aria-label="Toggle dark mode">
                {darkMode ? <Sun size={17} color="#fbbf24" /> : <Moon size={17} color="#94a3b8" />}
              </motion.button>

              {/* Desktop auth */}
              <div className="hidden lg:flex items-center gap-3">
                {!user ? (
                  <>
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                      onClick={() => setShowLogin(true)}
                      className="px-5 py-2.5 rounded-full text-sm font-medium text-white transition-all"
                      style={{ background: "rgba(255,255,255,0.05)", border: "1px solid rgba(255,255,255,0.1)" }}>
                      Log In
                    </motion.button>
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                      onClick={() => setShowLogin(true)}
                      className="px-5 py-2.5 rounded-full text-sm font-medium text-white transition-all"
                      style={{ background: "rgba(255,255,255,0.15)", border: "1px solid rgba(255,255,255,0.25)", backdropFilter: "blur(10px)" }}>
                      Sign Up
                    </motion.button>
                  </>
                ) : (
                  <div className="relative" ref={dropdownRef}>
                    <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                      onClick={() => setDropdownOpen(!dropdownOpen)}
                      className="flex items-center gap-2 p-1 pr-3 rounded-full border transition-all"
                      style={{ background: "rgba(255,255,255,0.08)", borderColor: "rgba(255,255,255,0.15)" }}>
                      {avatarUrl
                        ? <img src={avatarUrl} alt="avatar" className="w-8 h-8 rounded-full object-cover border border-emerald-500/30" />
                        : <div className="w-8 h-8 rounded-full flex items-center justify-center text-white font-semibold text-sm"
                            style={{ background: "linear-gradient(135deg,#10b981,#0ea5e9)" }}>
                            {displayName[0].toUpperCase()}
                          </div>
                      }
                      <ChevronDown size={14} className="text-white/70" />
                    </motion.button>

                    <AnimatePresence>
                      {dropdownOpen && (
                        <motion.div
                          initial={{ opacity: 0, y: 10, scale: 0.95 }}
                          animate={{ opacity: 1, y: 0, scale: 1 }}
                          exit={{ opacity: 0, y: 10, scale: 0.95 }}
                          transition={{ duration: 0.2 }}
                          className="absolute right-0 mt-3 w-60 rounded-2xl overflow-hidden shadow-2xl border"
                          style={{ background: "rgba(2,8,23,0.95)", borderColor: "rgba(255,255,255,0.15)", backdropFilter: "blur(20px)" }}>
                          <div className="p-5 border-b border-white/10">
                            <p className="text-sm font-bold text-white mb-0.5">{displayName}</p>
                            <p className="text-xs text-white/60">{displayEmail}</p>
                          </div>
                          <div className="p-2 flex flex-col gap-1">
                            {[
                              { icon: User,    label: "My Profile",  to: "/profile" },
                              { icon: MapPin,  label: "Saved Trips", to: "/profile" },
                              { icon: History, label: "Trip History", to: "/profile" },
                              { icon: Heart,   label: "Wishlist",    to: "/profile" },
                              { icon: Settings,label: "Settings",    to: "/profile" },
                            ].map((item, i) => (
                              <Link key={i} to={item.to} onClick={() => setDropdownOpen(false)}
                                className="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-white/70 hover:text-white hover:bg-white/10 transition-colors">
                                <item.icon size={16} className="text-emerald-400" /> {item.label}
                              </Link>
                            ))}
                            <div className="h-px bg-white/10 my-2 mx-2" />
                            <button onClick={handleLogout}
                              className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors text-left">
                              <LogOut size={16} /> Logout
                            </button>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                )}

                {/* Plan My Trip CTA */}
                <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}
                  onClick={handlePlanMyTrip}
                  className="flex items-center gap-2 btn-primary ml-2"
                  style={{ padding: "10px 24px", fontSize: "14px" }}>
                  <span>Plan My Trip</span>
                  <Plane size={15} />
                </motion.button>
              </div>

              {/* Mobile hamburger */}
              <motion.button whileTap={{ scale: 0.9 }} onClick={() => setMenuOpen(!menuOpen)}
                className="lg:hidden w-10 h-10 rounded-full flex items-center justify-center"
                style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)" }}
                aria-label="Toggle menu">
                {menuOpen ? <X size={18} className="text-white" /> : <Menu size={18} className="text-white" />}
              </motion.button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* ── Mobile Menu ──────────────────────────────────────────────────────── */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }} transition={{ duration: 0.3 }}
            className="fixed inset-0 z-40 lg:hidden overflow-y-auto"
            style={{ top: "80px" }}>
            <div className="glass-dark min-h-full p-6 flex flex-col gap-4 pb-20">

              {/* Mobile auth section */}
              <div className="flex flex-col gap-3 mb-6 pb-6 border-b border-white/10">
                {!user ? (
                  <>
                    <button onClick={() => { setMenuOpen(false); setShowLogin(true); }}
                      className="w-full py-3 rounded-xl bg-white/5 border border-white/10 text-white font-medium hover:bg-white/10 transition-colors">
                      Log In
                    </button>
                    <button onClick={() => { setMenuOpen(false); setShowLogin(true); }}
                      className="w-full py-3 rounded-xl text-white font-medium transition-all"
                      style={{ background: "linear-gradient(135deg,#10b981,#0ea5e9)" }}>
                      Sign Up
                    </button>
                  </>
                ) : (
                  <div className="flex flex-col gap-4">
                    <div className="flex items-center gap-4 bg-white/5 p-4 rounded-2xl border border-white/10">
                      {avatarUrl
                        ? <img src={avatarUrl} alt="avatar" className="w-12 h-12 rounded-full object-cover border-2 border-emerald-500/50" />
                        : <div className="w-12 h-12 rounded-full flex items-center justify-center text-white font-bold text-lg"
                            style={{ background: "linear-gradient(135deg,#10b981,#0ea5e9)" }}>
                            {displayName[0].toUpperCase()}
                          </div>
                      }
                      <div>
                        <p className="font-bold text-white">{displayName}</p>
                        <p className="text-xs text-emerald-400">{displayEmail}</p>
                      </div>
                    </div>
                    <Link to="/profile" onClick={() => setMenuOpen(false)}>
                      <button className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-white/5 border border-white/10 text-white font-medium hover:bg-white/10 transition-colors">
                        <User size={16} /> My Profile
                      </button>
                    </Link>
                    <button onClick={handleLogout}
                      className="w-full flex items-center justify-center gap-2 py-3 rounded-xl bg-red-500/10 text-red-400 font-medium hover:bg-red-500/20 transition-colors">
                      <LogOut size={16} /> Logout
                    </button>
                  </div>
                )}
              </div>

              {/* Mobile nav links */}
              {navLinks.map((link, i) => (
                <motion.button key={link.href}
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07 }}
                  onClick={() => scrollTo(link.href)}
                  className="text-left text-lg font-medium py-3 px-4 rounded-xl text-white/80 hover:text-white hover:bg-white/5 transition-all bg-transparent border-none cursor-pointer">
                  {link.label}
                </motion.button>
              ))}

              <motion.button initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
                onClick={handlePlanMyTrip} className="btn-primary mt-4">
                Plan My Trip ✈️
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ── Login Modal ──────────────────────────────────────────────────────── */}
      <LoginModal isOpen={showLogin} onClose={() => setShowLogin(false)} redirectTo="/results" />
    </>
  );
};

export default Navbar;
