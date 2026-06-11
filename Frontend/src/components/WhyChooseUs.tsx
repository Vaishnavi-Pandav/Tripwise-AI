import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { DollarSign, Lightbulb, Activity, Heart } from "lucide-react";

const featureCards = [
  {
    icon: DollarSign,
    title: "Transparent Pricing",
    description: "No hidden fees, no surprises. Full cost breakdown before you book.",
    color: "#10b981",
  },
  {
    icon: Lightbulb,
    title: "Smart Recommendations",
    description: "AI learns your travel style to give increasingly personalized suggestions.",
    color: "#0ea5e9",
  },
  {
    icon: Activity,
    title: "Real-Time Insights",
    description: "Live flight prices, hotel availability, and crowd levels at your destination.",
    color: "#f59e0b",
  },
  {
    icon: Heart,
    title: "Personalized Trips",
    description: "Every itinerary is unique — crafted around your passions, pace, and preferences.",
    color: "#8b5cf6",
  },
];

const WhyChooseUs = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section ref={ref} className="relative section-padding" style={{ padding: "100px 0", overflow: "hidden" }}>
      {/* Background */}
      <div className="absolute inset-0" style={{ background: "linear-gradient(135deg, rgba(2,8,23,0.95) 0%, rgba(15,32,64,0.8) 50%, rgba(2,8,23,0.95) 100%)" }} />

      {/* Floating blobs */}
      <motion.div
        className="absolute w-80 h-80 rounded-full opacity-10"
        style={{ background: "radial-gradient(circle, #10b981, transparent)", top: "10%", right: "5%" }}
        animate={{ y: [0, -30, 0], scale: [1, 1.1, 1] }}
        transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute w-60 h-60 rounded-full opacity-10"
        style={{ background: "radial-gradient(circle, #0ea5e9, transparent)", bottom: "10%", left: "5%" }}
        animate={{ y: [0, 20, 0], scale: [1, 0.9, 1] }}
        transition={{ duration: 6, repeat: Infinity, ease: "easeInOut", delay: 2 }}
      />

      <div className="container-custom relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: Image with decorative elements */}
          <motion.div
            initial={{ opacity: 0, x: -50 }}
            animate={inView ? { opacity: 1, x: 0 } : {}}
            transition={{ duration: 0.9, ease: "easeOut" }}
            className="relative"
          >
            {/* Main image area */}
            <div className="relative rounded-3xl overflow-hidden" style={{ height: "500px" }}>
              <img
                src="https://images.unsplash.com/photo-1488085061387-422e29b40080?w=800&auto=format&fit=crop"
                alt="Happy travelers planning their trip with TripWise AI"
                className="w-full h-full object-cover"
              />
              <div
                className="absolute inset-0"
                style={{ background: "linear-gradient(135deg, rgba(2,8,23,0.2) 0%, rgba(10,22,40,0.4) 100%)" }}
              />
            </div>

            {/* Floating stat card #1 */}
            <motion.div
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 5, repeat: Infinity, ease: "easeInOut" }}
              className="absolute -top-6 -right-6 glass-dark rounded-2xl p-4"
              style={{ width: "160px" }}
            >
              <div className="text-2xl font-black text-white" style={{ lineHeight: 1 }}>98%</div>
              <div className="text-xs mt-1" style={{ color: "#34d399" }}>Satisfaction Rate</div>
              <div className="flex gap-0.5 mt-2">
                {[...Array(5)].map((_, i) => (
                  <span key={i} style={{ color: "#f59e0b", fontSize: "12px" }}>★</span>
                ))}
              </div>
            </motion.div>

            {/* Floating stat card #2 */}
            <motion.div
              animate={{ y: [0, 12, 0] }}
              transition={{ duration: 7, repeat: Infinity, ease: "easeInOut", delay: 1 }}
              className="absolute -bottom-6 -left-6 glass-dark rounded-2xl p-4"
              style={{ width: "180px" }}
            >
              <div className="flex items-center gap-2 mb-2">
                <div className="w-8 h-8 rounded-full flex items-center justify-center text-lg"
                  style={{ background: "linear-gradient(135deg, #10b981, #0ea5e9)" }}>
                  ✈️
                </div>
                <div>
                  <div className="text-white font-bold text-sm">New Trip!</div>
                  <div style={{ color: "rgba(255,255,255,0.5)", fontSize: "11px" }}>Just booked</div>
                </div>
              </div>
              <div className="text-xs font-medium" style={{ color: "#34d399" }}>Bali, Indonesia · 7 days</div>
            </motion.div>

            {/* Decorative ring */}
            <div
              className="absolute -inset-4 rounded-3xl pointer-events-none"
              style={{ border: "1px solid rgba(16,185,129,0.15)", borderRadius: "32px" }}
            />
          </motion.div>

          {/* Right: Feature cards */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6 }}
              className="section-badge mb-4"
            >
              💎 Why TripWise
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="font-playfair text-white mb-4"
              style={{ fontSize: "clamp(28px, 3.5vw, 48px)", fontWeight: 700, letterSpacing: "-0.02em" }}
            >
              Why Choose <span className="gradient-text">TripWise AI</span>?
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.6, delay: 0.2 }}
              style={{ color: "rgba(255,255,255,0.5)", fontSize: "16px", lineHeight: 1.8, marginBottom: "40px" }}
            >
              We combine the power of AI with deep travel expertise to deliver 
              experiences that go beyond ordinary travel planning.
            </motion.p>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {featureCards.map((card, i) => {
                const Icon = card.icon;
                return (
                  <motion.div
                    key={card.title}
                    initial={{ opacity: 0, y: 30 }}
                    animate={inView ? { opacity: 1, y: 0 } : {}}
                    transition={{ duration: 0.6, delay: 0.3 + i * 0.12 }}
                    className="glass-card rounded-2xl p-5 group"
                  >
                    <div
                      className="w-10 h-10 rounded-xl flex items-center justify-center mb-3"
                      style={{ background: `${card.color}20`, border: `1px solid ${card.color}40` }}
                    >
                      <Icon size={18} color={card.color} />
                    </div>
                    <h4 className="text-white font-semibold mb-2" style={{ fontSize: "15px" }}>
                      {card.title}
                    </h4>
                    <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "13px", lineHeight: 1.7 }}>
                      {card.description}
                    </p>
                  </motion.div>
                );
              })}
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default WhyChooseUs;
