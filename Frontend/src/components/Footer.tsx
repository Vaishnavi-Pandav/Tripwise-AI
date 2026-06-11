import { motion } from "framer-motion";
import { Plane, Globe, Rss, Camera, Play, Link, Mail, MapPin, Phone, ArrowRight, Send } from "lucide-react";

const Footer = () => {
  const scrollTo = (href: string) => {
    document.querySelector(href)?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <footer
      className="relative overflow-hidden"
      style={{ background: "rgba(2,5,15,0.98)", borderTop: "1px solid rgba(255,255,255,0.06)" }}
    >
      {/* Watermark */}
      <div
        className="absolute bottom-0 left-0 right-0 flex items-end justify-center pointer-events-none select-none overflow-hidden"
        style={{ paddingBottom: "-40px" }}
      >
        <span
          style={{
            fontSize: "clamp(80px, 18vw, 220px)",
            fontWeight: 900,
            color: "white",
            opacity: 0.02,
            fontFamily: "'Playfair Display', serif",
            letterSpacing: "-0.04em",
            lineHeight: 0.85,
            transform: "translateY(20%)",
          }}
        >
          TRIPWISE AI
        </span>
      </div>

      <div className="container-custom relative z-10">
        {/* Main footer grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-12 pt-20 pb-16">
          {/* Brand column */}
          <div className="lg:col-span-1">
            <div className="flex items-center gap-3 mb-6">
              <div
                className="w-11 h-11 rounded-xl flex items-center justify-center"
                style={{ background: "linear-gradient(135deg, #10b981, #0ea5e9)" }}
              >
                <Plane size={20} color="white" />
              </div>
              <div>
                <span className="text-xl font-bold text-white" style={{ letterSpacing: "-0.02em" }}>
                  TripWise<span className="gradient-text">AI</span>
                </span>
                <div className="text-xs text-emerald-400 font-medium" style={{ marginTop: "-2px", letterSpacing: "0.05em" }}>
                  TRAVEL SMARTER
                </div>
              </div>
            </div>
            <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "14px", lineHeight: 1.8, marginBottom: "24px" }}>
              Your AI-powered travel companion for creating perfect journeys — personalized, optimized, and unforgettable.
            </p>

            {/* Social links */}
            <div className="flex gap-3">
              {[
                { icon: Camera, label: "Instagram" },
                { icon: Globe, label: "Twitter" },
                { icon: Link, label: "Facebook" },
                { icon: Play, label: "YouTube" },
                { icon: Rss, label: "LinkedIn" },
              ].map(({ icon: Icon, label }) => (
                <motion.a
                  key={label}
                  href="#"
                  aria-label={label}
                  whileHover={{ scale: 1.15, y: -3 }}
                  className="w-9 h-9 rounded-xl flex items-center justify-center transition-all duration-300"
                  style={{
                    background: "rgba(255,255,255,0.05)",
                    border: "1px solid rgba(255,255,255,0.08)",
                    color: "rgba(255,255,255,0.4)",
                  }}
                  onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = "#10b981"; (e.currentTarget as HTMLElement).style.borderColor = "rgba(16,185,129,0.4)"; }}
                  onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = "rgba(255,255,255,0.4)"; (e.currentTarget as HTMLElement).style.borderColor = "rgba(255,255,255,0.08)"; }}
                >
                  <Icon size={15} />
                </motion.a>
              ))}
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-6" style={{ fontSize: "14px", letterSpacing: "0.05em", textTransform: "uppercase" }}>
              Quick Links
            </h4>
            <ul className="space-y-3">
              {[
                { label: "Home", href: "#home" },
                { label: "Destinations", href: "#destinations" },
                { label: "AI Planner", href: "#ai-planner" },
                { label: "Travel Packages", href: "#packages" },
                { label: "Reviews", href: "#reviews" },
                { label: "Travel Blog", href: "#blog" },
              ].map((link) => (
                <li key={link.href}>
                  <button
                    onClick={() => scrollTo(link.href)}
                    className="flex items-center gap-2 text-sm transition-all duration-200 bg-transparent border-none cursor-pointer"
                    style={{ color: "rgba(255,255,255,0.45)", padding: 0 }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = "#10b981"; }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = "rgba(255,255,255,0.45)"; }}
                  >
                    <ArrowRight size={12} />
                    {link.label}
                  </button>
                </li>
              ))}
            </ul>
          </div>

          {/* Contact */}
          <div>
            <h4 className="text-white font-semibold mb-6" style={{ fontSize: "14px", letterSpacing: "0.05em", textTransform: "uppercase" }}>
              Contact Us
            </h4>
            <div className="space-y-4">
              {[
                { icon: MapPin, text: "Bangalore, Karnataka, India" },
                { icon: Mail, text: "hello@tripwiseai.com" },
                { icon: Phone, text: "+91 98765 43210" },
              ].map(({ icon: Icon, text }) => (
                <div key={text} className="flex items-start gap-3">
                  <div
                    className="w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 mt-0.5"
                    style={{ background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)" }}
                  >
                    <Icon size={14} color="#10b981" />
                  </div>
                  <span style={{ color: "rgba(255,255,255,0.45)", fontSize: "14px", lineHeight: 1.6 }}>{text}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Newsletter */}
          <div>
            <h4 className="text-white font-semibold mb-2" style={{ fontSize: "14px", letterSpacing: "0.05em", textTransform: "uppercase" }}>
              Newsletter
            </h4>
            <p style={{ color: "rgba(255,255,255,0.4)", fontSize: "13px", lineHeight: 1.7, marginBottom: "20px" }}>
              Get travel tips, AI insights, and exclusive deals delivered weekly.
            </p>
            <div className="flex gap-2">
              <input
                id="newsletter-email"
                type="email"
                placeholder="Enter your email"
                className="flex-1 search-input"
                style={{ borderRadius: "12px", fontSize: "13px" }}
              />
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                id="newsletter-submit-btn"
                className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0"
                style={{
                  background: "linear-gradient(135deg, #10b981, #0ea5e9)",
                  border: "none",
                  cursor: "pointer",
                }}
              >
                <Send size={15} color="white" />
              </motion.button>
            </div>
            <p style={{ color: "rgba(255,255,255,0.25)", fontSize: "11px", marginTop: "10px" }}>
              No spam. Unsubscribe at any time.
            </p>
          </div>
        </div>

        {/* Divider */}
        <div style={{ height: "1px", background: "rgba(255,255,255,0.06)", margin: "0 0 24px" }} />

        {/* Copyright row */}
        <div
          className="flex flex-col sm:flex-row items-center justify-between gap-4 pb-8"
          style={{ color: "rgba(255,255,255,0.25)", fontSize: "13px" }}
        >
          <span>© 2026 TripWise AI. All rights reserved.</span>
          <div className="flex gap-6">
            {["Privacy Policy", "Terms of Service", "Cookie Policy"].map((t) => (
              <a
                key={t}
                href="#"
                className="hover:text-white transition-colors duration-200"
                style={{ color: "inherit", textDecoration: "none" }}
              >
                {t}
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
