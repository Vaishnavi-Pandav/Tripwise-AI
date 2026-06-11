import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Sparkles, ArrowRight, MessageCircle } from "lucide-react";
import { Link } from "react-router-dom";

const CTASection = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });


  return (
    <section ref={ref} id="contact" className="relative section-padding" style={{ padding: "80px 0", overflow: "hidden" }}>
      <div className="container-custom">
        <motion.div
          initial={{ opacity: 0, y: 40, scale: 0.98 }}
          animate={inView ? { opacity: 1, y: 0, scale: 1 } : {}}
          transition={{ duration: 0.8 }}
          className="relative rounded-3xl overflow-hidden"
          style={{ padding: "80px 48px", textAlign: "center" }}
        >
          {/* Gradient background */}
          <div
            className="absolute inset-0"
            style={{
              background: "linear-gradient(135deg, rgba(16,185,129,0.15) 0%, rgba(10,22,40,0.95) 40%, rgba(14,165,233,0.15) 100%)",
              backdropFilter: "blur(20px)",
              border: "1px solid rgba(255,255,255,0.1)",
              borderRadius: "24px",
            }}
          />

          {/* Animated orbs */}
          <motion.div
            animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
            transition={{ duration: 5, repeat: Infinity }}
            className="absolute w-80 h-80 rounded-full -top-20 -left-20 pointer-events-none"
            style={{ background: "radial-gradient(circle, rgba(16,185,129,0.2), transparent)" }}
          />
          <motion.div
            animate={{ scale: [1, 1.3, 1], opacity: [0.2, 0.4, 0.2] }}
            transition={{ duration: 7, repeat: Infinity, delay: 2 }}
            className="absolute w-72 h-72 rounded-full -bottom-16 -right-16 pointer-events-none"
            style={{ background: "radial-gradient(circle, rgba(14,165,233,0.2), transparent)" }}
          />

          {/* Watermark */}
          <div
            className="absolute inset-0 flex items-center justify-center pointer-events-none select-none"
            style={{
              fontSize: "clamp(48px, 10vw, 140px)",
              fontWeight: 900,
              color: "white",
              opacity: 0.025,
              fontFamily: "'Playfair Display', serif",
              letterSpacing: "-0.04em",
            }}
          >
            TRIPWISE AI
          </div>

          {/* Content */}
          <div className="relative z-10">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.2 }}
              className="section-badge mx-auto mb-6"
            >
              🚀 Start Planning Today
            </motion.div>

            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.3 }}
              className="font-playfair text-white mb-5"
              style={{ fontSize: "clamp(32px, 5vw, 64px)", fontWeight: 700, letterSpacing: "-0.025em", lineHeight: 1.1 }}
            >
              Your Next Adventure{" "}
              <span className="gradient-text">Starts Here</span>
            </motion.h2>

            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.4 }}
              style={{ color: "rgba(255,255,255,0.55)", fontSize: "18px", maxWidth: "500px", margin: "0 auto 40px", lineHeight: 1.7 }}
            >
              Join 50,000+ travelers who've discovered the future of travel planning. 
              Let AI craft your perfect trip today.
            </motion.p>

            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.5 }}
              className="flex flex-col sm:flex-row items-center justify-center gap-4"
            >
              <Link to="/results">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.97 }}
                  id="cta-generate-btn"
                  className="btn-primary flex items-center gap-2"
                  style={{ padding: "16px 40px", fontSize: "16px" }}
                >
                  <Sparkles size={18} />
                  <span>Generate AI Trip</span>
                </motion.button>
              </Link>
              <Link to="/contact">
                <motion.button
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.97 }}
                  id="cta-contact-btn"
                  className="btn-outline flex items-center gap-2"
                  style={{ padding: "15px 40px", fontSize: "16px" }}
                >
                  <MessageCircle size={18} />
                  Contact Us
                  <ArrowRight size={16} />
                </motion.button>
              </Link>
            </motion.div>

            {/* Trust row */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : {}}
              transition={{ delay: 0.7 }}
              className="flex flex-wrap items-center justify-center gap-8 mt-12"
              style={{ color: "rgba(255,255,255,0.35)", fontSize: "13px" }}
            >
              <span>🔒 No credit card required</span>
              <span>⚡ Instant results</span>
              <span>🌍 500+ destinations</span>
              <span>💯 Free to start</span>
            </motion.div>
          </div>
        </motion.div>
      </div>
    </section>
  );
};

export default CTASection;
