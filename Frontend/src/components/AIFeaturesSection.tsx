import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Route, PiggyBank, Gem, Package, CloudSun, BarChart3 } from "lucide-react";

const features = [
  {
    id: "itinerary-gen",
    icon: Route,
    title: "AI Itinerary Generator",
    description: "Day-by-day personalized travel plans built from your preferences, budget, and travel style.",
    gradient: "linear-gradient(135deg, #10b981 0%, #0ea5e9 100%)",
    glow: "rgba(16,185,129,0.4)",
    tag: "Most Popular",
  },
  {
    id: "budget-optimizer",
    icon: PiggyBank,
    title: "Budget Optimizer",
    description: "AI allocates your budget intelligently across accommodation, food, activities, and transport.",
    gradient: "linear-gradient(135deg, #f59e0b 0%, #ef4444 100%)",
    glow: "rgba(245,158,11,0.3)",
    tag: null,
  },
  {
    id: "hidden-gems",
    icon: Gem,
    title: "Hidden Gems Discovery",
    description: "Uncover secret spots, local restaurants, and off-the-beaten-path experiences missed by most tourists.",
    gradient: "linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%)",
    glow: "rgba(139,92,246,0.3)",
    tag: "🔥 Trending",
  },
  {
    id: "packing-list",
    icon: Package,
    title: "Smart Packing List",
    description: "AI-generated packing lists tailored to your destination, weather, duration, and activities.",
    gradient: "linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%)",
    glow: "rgba(14,165,233,0.3)",
    tag: null,
  },
  {
    id: "weather-intel",
    icon: CloudSun,
    title: "Weather Intelligence",
    description: "Real-time and predictive weather insights to plan activities and pack appropriately for your trip.",
    gradient: "linear-gradient(135deg, #34d399 0%, #10b981 100%)",
    glow: "rgba(52,211,153,0.3)",
    tag: null,
  },
  {
    id: "dest-compare",
    icon: BarChart3,
    title: "Destination Comparison",
    description: "Compare destinations side-by-side on cost, weather, safety, crowd levels, and AI recommendations.",
    gradient: "linear-gradient(135deg, #f43f5e 0%, #f97316 100%)",
    glow: "rgba(244,63,94,0.3)",
    tag: null,
  },
];

const AIFeaturesSection = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="ai-planner" ref={ref} className="relative section-padding" style={{ padding: "100px 0", background: "rgba(10,22,40,0.5)" }}>
      {/* Decorative blobs */}
      <div className="orb orb-purple absolute w-96 h-96 top-0 right-0 opacity-15" />
      <div className="orb orb-emerald absolute w-80 h-80 bottom-0 left-10 opacity-15" />

      <div className="container-custom relative z-10">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="section-badge mx-auto mb-4"
          >
            🤖 AI Capabilities
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="font-playfair text-white"
            style={{ fontSize: "clamp(30px, 4vw, 52px)", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: "16px" }}
          >
            Powered by <span className="gradient-text">AI Features</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            style={{ color: "rgba(255,255,255,0.5)", fontSize: "17px", maxWidth: "500px", margin: "0 auto", lineHeight: 1.7 }}
          >
            Everything you need for a perfect trip, supercharged by artificial intelligence
          </motion.p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map((feature, i) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={feature.id}
                initial={{ opacity: 0, y: 40, scale: 0.97 }}
                animate={inView ? { opacity: 1, y: 0, scale: 1 } : {}}
                transition={{ duration: 0.65, delay: i * 0.1 }}
                className="glass-card rounded-2xl p-7 relative group"
              >
                {/* Tag */}
                {feature.tag && (
                  <div
                    className="absolute top-5 right-5 text-xs font-bold px-2.5 py-1 rounded-full"
                    style={{
                      background: "rgba(16,185,129,0.15)",
                      border: "1px solid rgba(16,185,129,0.3)",
                      color: "#34d399",
                    }}
                  >
                    {feature.tag}
                  </div>
                )}

                {/* Icon */}
                <motion.div
                  whileHover={{ scale: 1.12, rotate: 8 }}
                  className="w-14 h-14 rounded-2xl flex items-center justify-center mb-5"
                  style={{
                    background: feature.gradient,
                    boxShadow: `0 8px 32px ${feature.glow}`,
                    transition: "box-shadow 0.3s ease",
                  }}
                >
                  <Icon size={24} color="white" strokeWidth={2} />
                </motion.div>

                {/* Content */}
                <h3 className="text-white font-semibold mb-3" style={{ fontSize: "18px", letterSpacing: "-0.01em" }}>
                  {feature.title}
                </h3>
                <p style={{ color: "rgba(255,255,255,0.5)", fontSize: "14px", lineHeight: 1.75 }}>
                  {feature.description}
                </p>

                {/* Hover glow line */}
                <div
                  className="absolute inset-0 rounded-2xl opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none"
                  style={{
                    background: `radial-gradient(circle at 50% 0%, ${feature.glow} 0%, transparent 60%)`,
                  }}
                />
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
};

export default AIFeaturesSection;
