import { useRef, useState } from "react";
import { motion, useScroll, useTransform } from "framer-motion";
import { ChevronDown, ArrowRight } from "lucide-react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import LoginModal from "./LoginModal";

const HeroSection = () => {
  const ref = useRef<HTMLDivElement>(null);
  const { scrollYProgress } = useScroll({ target: ref, offset: ["start start", "end start"] });
  const y = useTransform(scrollYProgress, [0, 1], ["0%", "30%"]);
  const opacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);
  const { user } = useAuth();
  const navigate = useNavigate();
  const [showLogin, setShowLogin] = useState(false);

  const handleBeginJourney = () => {
    if (user) {
      navigate("/results");
    } else {
      setShowLogin(true);
    }
  };

  const scrollToDestinations = () => {
    document.querySelector("#destinations")?.scrollIntoView({ behavior: "smooth" });
  };

  return (
    <>
      <section id="home" ref={ref} className="relative h-screen w-full flex flex-col items-center justify-center overflow-hidden bg-black">
        {/* Parallax & Zoom Background */}
        <motion.div style={{ y }} className="absolute inset-0 z-0">
          <motion.img
            initial={{ scale: 1 }}
            animate={{ scale: 1.05 }}
            transition={{ duration: 20, ease: "linear", repeat: Infinity, repeatType: "reverse" }}
            src="/hero-bg.png"
            alt="Cinematic travel landscape with mountains beaches and cityscapes"
            className="w-full h-full object-cover object-center"
          />
          <div className="absolute inset-0 bg-black/30" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#020817] via-transparent to-black/40" />
        </motion.div>

        {/* Watermark text */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 2, delay: 0.5 }}
          className="absolute inset-0 flex items-center justify-center pointer-events-none z-10 overflow-hidden"
        >
          <span
            className="text-white select-none opacity-[0.03]"
            style={{
              fontSize: "clamp(100px, 25vw, 350px)",
              fontWeight: 800,
              letterSpacing: "0.08em",
              fontFamily: "'Inter', sans-serif",
              lineHeight: 1,
              whiteSpace: "nowrap",
            }}
          >
            EXPLORE
          </span>
        </motion.div>

        <motion.div style={{ opacity }} className="relative z-20 w-full px-4 mt-16">
          <div className="max-w-[800px] mx-auto flex flex-col items-center text-center">
            <motion.div
              initial={{ opacity: 0, y: 40 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 1.2, delay: 0.2, ease: [0.25, 0.4, 0.25, 1] }}
              className="flex flex-col items-center w-full"
            >
              <h1
                className="font-playfair text-white mb-8"
                style={{
                  fontSize: "clamp(2.5rem, 5vw + 1rem, 8rem)",
                  fontWeight: 500,
                  lineHeight: 1.1,
                  letterSpacing: "-0.01em",
                  textShadow: "0 10px 40px rgba(0,0,0,0.5)",
                }}
              >
                Travel Smarter.<br />
                <span className="italic text-white/90">Explore Further.</span>
              </h1>

              <p
                className="text-white/70 font-light tracking-wide mb-12 max-w-md"
                style={{
                  fontSize: "clamp(0.9rem, 1.2vw, 1.1rem)",
                  lineHeight: 1.8,
                  fontFamily: "'Inter', sans-serif",
                  textShadow: "0 2px 10px rgba(0,0,0,0.5)",
                }}
              >
                Experience the world's most breathtaking destinations.
                Curated by experts, elevated by intelligence.
              </p>

              {/* CTA Button — gates on auth */}
              <motion.button
                onClick={handleBeginJourney}
                whileHover={{ scale: 1.03 }}
                whileTap={{ scale: 0.97 }}
                className="glass-card flex items-center justify-center gap-3 text-white px-8 py-4 rounded-full font-medium tracking-widest text-xs uppercase transition-all duration-300"
                style={{
                  background: "rgba(255, 255, 255, 0.08)",
                  border: "1px solid rgba(255, 255, 255, 0.15)",
                  boxShadow: "0 20px 40px rgba(0,0,0,0.3), inset 0 0 0 1px rgba(255,255,255,0.05)",
                  backdropFilter: "blur(12px)",
                  fontFamily: "'Inter', sans-serif",
                }}
              >
                Begin Your Journey
                <ArrowRight size={14} strokeWidth={1.5} />
              </motion.button>
            </motion.div>
          </div>
        </motion.div>

        {/* Scroll indicator */}
        <motion.button
          onClick={scrollToDestinations}
          initial={{ opacity: 0 }}
          animate={{ opacity: 1, y: [0, 8, 0] }}
          transition={{ duration: 2, repeat: Infinity, delay: 1.5 }}
          className="absolute bottom-12 left-1/2 -translate-x-1/2 z-20 flex flex-col items-center gap-3 bg-transparent border-none cursor-pointer group"
          aria-label="Scroll down"
        >
          <span className="text-[10px] text-white/40 tracking-[0.25em] uppercase group-hover:text-white/80 transition-colors font-medium">Scroll</span>
          <ChevronDown size={20} className="text-white/40 group-hover:text-white/80 transition-colors" strokeWidth={1.5} />
        </motion.button>
      </section>

      {/* Login modal */}
      <LoginModal
        isOpen={showLogin}
        onClose={() => setShowLogin(false)}
        redirectTo="/results"
      />
    </>
  );
};

export default HeroSection;
