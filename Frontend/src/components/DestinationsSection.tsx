import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { MapPin, TrendingUp, ArrowRight } from "lucide-react";

const destinations = [
  {
    id: "goa",
    name: "Goa",
    country: "India",
    image: "/goa.png",
    budget: "₹8,000 – ₹25,000",
    season: "Oct – Mar",
    aiScore: 9.4,
    tag: "Beach Bliss",
    tagColor: "#0ea5e9",
  },
  {
    id: "bali",
    name: "Bali",
    country: "Indonesia",
    image: "/bali.png",
    budget: "₹35,000 – ₹80,000",
    season: "Apr – Oct",
    aiScore: 9.7,
    tag: "Tropical Paradise",
    tagColor: "#10b981",
  },
  {
    id: "switzerland",
    name: "Switzerland",
    country: "Europe",
    image: "/switzerland.png",
    budget: "₹2.5L – ₹5L",
    season: "Jun – Sep",
    aiScore: 9.8,
    tag: "Alpine Wonder",
    tagColor: "#8b5cf6",
  },
  {
    id: "dubai",
    name: "Dubai",
    country: "UAE",
    image: "/dubai.png",
    budget: "₹60,000 – ₹1.5L",
    season: "Nov – Mar",
    aiScore: 9.5,
    tag: "Luxury City",
    tagColor: "#f59e0b",
  },
  {
    id: "manali",
    name: "Manali",
    country: "India",
    image: "/manali.png",
    budget: "₹12,000 – ₹30,000",
    season: "Mar – Jun",
    aiScore: 9.1,
    tag: "Mountain Magic",
    tagColor: "#34d399",
  },
  {
    id: "japan",
    name: "Japan",
    country: "East Asia",
    image: "https://images.unsplash.com/photo-1492571350019-22de08371fd3?w=800&auto=format&fit=crop",
    budget: "₹1.2L – ₹2.5L",
    season: "Mar – May",
    aiScore: 9.9,
    tag: "Cultural Icon",
    tagColor: "#f43f5e",
  },
];

const DestinationsSection = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="destinations" ref={ref} className="relative section-padding" style={{ padding: "100px 0" }}>
      <div className="container-custom">
        {/* Header */}
        <div className="flex flex-col md:flex-row md:items-end md:justify-between mb-14 gap-4">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="section-badge mb-4"
            >
              🌍 Top Picks
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="font-playfair text-white"
              style={{ fontSize: "clamp(30px, 4vw, 50px)", fontWeight: 700, letterSpacing: "-0.02em" }}
            >
              Popular <span className="gradient-text">Destinations</span>
            </motion.h2>
          </div>
          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            style={{ color: "rgba(255,255,255,0.45)", fontSize: "14px", maxWidth: "300px", lineHeight: 1.7 }}
          >
            Handpicked by AI based on traveler reviews, budget value, and seasonal availability
          </motion.p>
        </div>

        {/* Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {destinations.map((dest, i) => (
            <motion.div
              key={dest.id}
              initial={{ opacity: 0, y: 50 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.65, delay: i * 0.1 }}
              className="destination-card group"
              style={{ height: "360px" }}
            >
              {/* Image */}
              <img
                src={dest.image}
                alt={`${dest.name}, ${dest.country} travel destination`}
                className="w-full h-full object-cover"
                style={{ borderRadius: "20px" }}
              />
              {/* Overlay */}
              <div className="overlay rounded-2xl" />

              {/* Top tag + AI score */}
              <div className="absolute top-4 left-4 right-4 flex justify-between items-center">
                <span
                  className="text-xs font-bold px-3 py-1.5 rounded-full"
                  style={{
                    background: `${dest.tagColor}22`,
                    border: `1px solid ${dest.tagColor}55`,
                    color: dest.tagColor,
                    backdropFilter: "blur(8px)",
                  }}
                >
                  {dest.tag}
                </span>
                <div
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-full"
                  style={{ background: "rgba(0,0,0,0.5)", backdropFilter: "blur(8px)" }}
                >
                  <TrendingUp size={11} color="#10b981" />
                  <span className="text-xs font-bold text-white">{dest.aiScore} AI Score</span>
                </div>
              </div>

              {/* Bottom content */}
              <div className="absolute bottom-0 left-0 right-0 p-5">
                <div className="flex items-end justify-between">
                  <div>
                    <div className="flex items-center gap-2 mb-1">
                      <MapPin size={13} color="#10b981" />
                      <span className="text-xs text-white/60">{dest.country}</span>
                    </div>
                    <h3 className="text-white font-bold text-2xl mb-2" style={{ letterSpacing: "-0.02em" }}>
                      {dest.name}
                    </h3>
                    <div className="flex items-center gap-4 text-xs text-white/60">
                      <span><span style={{ color: "#34d399" }}>₹</span> {dest.budget}</span>
                      <span>⛅ {dest.season}</span>
                    </div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    id={`explore-${dest.id}-btn`}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-full font-semibold text-sm opacity-0 group-hover:opacity-100 transition-all duration-300 translate-y-2 group-hover:translate-y-0"
                    style={{
                      background: "linear-gradient(135deg, #10b981, #0ea5e9)",
                      color: "white",
                      border: "none",
                      cursor: "pointer",
                    }}
                  >
                    Explore
                    <ArrowRight size={14} />
                  </motion.button>
                </div>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default DestinationsSection;
