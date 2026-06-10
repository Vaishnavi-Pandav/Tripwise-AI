import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Moon, Sun, Menu, X, Plane } from "lucide-react";

interface NavbarProps {
  darkMode: boolean;
  setDarkMode: (v: boolean) => void;
}

const navLinks = [
  { label: "Home", href: "#home" },
  { label: "Destinations", href: "#destinations" },
  { label: "AI Planner", href: "#ai-planner" },
  { label: "Packages", href: "#packages" },
  { label: "Reviews", href: "#reviews" },
  { label: "Contact", href: "#contact" },
];

const Navbar = ({ darkMode, setDarkMode }: NavbarProps) => {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 50);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  const scrollTo = (href: string) => {
    setMenuOpen(false);
    const el = document.querySelector(href);
    if (el) el.scrollIntoView({ behavior: "smooth", block: "start" });
  };

  return (
    <>
      <motion.nav
        initial={{ y: -80, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className={`fixed top-0 left-0 right-0 z-50 transition-all duration-500 ${
          scrolled
            ? "glass-dark shadow-2xl shadow-black/40"
            : "bg-transparent"
        }`}
        style={{ borderBottom: scrolled ? "1px solid rgba(255,255,255,0.08)" : "none" }}
      >
        <div className="container-custom">
          <div className="flex items-center justify-between h-20">
            {/* Logo */}
            <motion.div
              whileHover={{ scale: 1.03 }}
              className="flex items-center gap-3 cursor-pointer"
              onClick={() => scrollTo("#home")}
            >
              <div className="relative">
                <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{ background: "linear-gradient(135deg, #10b981, #0ea5e9)" }}>
                  <Plane size={20} color="white" />
                </div>
                <div className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
              </div>
              <div>
                <span className="text-xl font-bold text-white" style={{ fontFamily: "'Inter', sans-serif", letterSpacing: "-0.02em" }}>
                  TripWise<span className="gradient-text">AI</span>
                </span>
                <div className="text-xs text-emerald-400 font-medium" style={{ marginTop: "-2px", letterSpacing: "0.05em" }}>
                  TRAVEL SMARTER
                </div>
              </div>
            </motion.div>

            {/* Desktop Nav */}
            <div className="hidden lg:flex items-center gap-8 nav-links-desktop" style={{ display: "flex" }}>
              {navLinks.map((link) => (
                <button
                  key={link.href}
                  onClick={() => scrollTo(link.href)}
                  className="nav-link bg-transparent border-none"
                >
                  {link.label}
                </button>
              ))}
            </div>

            {/* Right controls */}
            <div className="flex items-center gap-4">
              {/* Dark Mode Toggle */}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={() => setDarkMode(!darkMode)}
                className="w-10 h-10 rounded-full flex items-center justify-center transition-all duration-300 border"
                style={{
                  background: "rgba(255,255,255,0.06)",
                  borderColor: "rgba(255,255,255,0.12)",
                }}
                aria-label="Toggle dark mode"
              >
                {darkMode ? (
                  <Sun size={17} color="#fbbf24" />
                ) : (
                  <Moon size={17} color="#94a3b8" />
                )}
              </motion.button>

              {/* CTA Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => scrollTo("#hero-form")}
                className="hidden lg:flex items-center gap-2 btn-primary"
                style={{ padding: "10px 24px", fontSize: "14px" }}
              >
                <span>Plan My Trip</span>
                <Plane size={15} />
              </motion.button>

              {/* Mobile menu toggle */}
              <motion.button
                whileTap={{ scale: 0.9 }}
                onClick={() => setMenuOpen(!menuOpen)}
                className="lg:hidden w-10 h-10 rounded-full flex items-center justify-center"
                style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)" }}
                aria-label="Toggle menu"
              >
                {menuOpen ? <X size={18} /> : <Menu size={18} />}
              </motion.button>
            </div>
          </div>
        </div>
      </motion.nav>

      {/* Mobile Menu */}
      <AnimatePresence>
        {menuOpen && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            transition={{ duration: 0.3 }}
            className="fixed inset-0 z-40 lg:hidden"
            style={{ top: "80px" }}
          >
            <div className="glass-dark h-full p-6 flex flex-col gap-4">
              {navLinks.map((link, i) => (
                <motion.button
                  key={link.href}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: i * 0.07 }}
                  onClick={() => scrollTo(link.href)}
                  className="text-left text-lg font-medium py-3 px-4 rounded-xl text-white/80 hover:text-white hover:bg-white/5 transition-all bg-transparent border-none cursor-pointer"
                >
                  {link.label}
                </motion.button>
              ))}
              <motion.button
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.4 }}
                onClick={() => scrollTo("#hero-form")}
                className="btn-primary mt-4"
              >
                <span>Plan My Trip ✈️</span>
              </motion.button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Navbar;
