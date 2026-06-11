import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { ClipboardList, Brain, Shield } from "lucide-react";

const steps = [
  {
    icon: ClipboardList,
    step: "01",
    title: "Enter Trip Preferences",
    description:
      "Tell us your dream destination, budget, travel dates, and interests. Our AI understands your unique travel style.",
    gradient: "from-emerald-500 to-teal-500",
    glow: "rgba(16,185,129,0.3)",
  },
  {
    icon: Brain,
    step: "02",
    title: "AI Builds Your Plan",
    description:
      "Our advanced AI analyzes thousands of data points to craft a personalized, day-by-day itinerary optimized for your needs.",
    gradient: "from-blue-500 to-cyan-500",
    glow: "rgba(14,165,233,0.3)",
  },
  {
    icon: Shield,
    step: "03",
    title: "Travel with Confidence",
    description:
      "Get real-time updates, smart packing lists, and 24/7 AI support throughout your entire journey.",
    gradient: "from-violet-500 to-purple-500",
    glow: "rgba(167,139,250,0.3)",
  },
];

const HowItWorks = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section ref={ref} className="relative section-padding" style={{ padding: "100px 0", background: "rgba(10,22,40,0.5)" }}>
      {/* Section heading */}
      <div className="container-custom">
        <div className="text-center mb-16">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6 }}
            className="section-badge mx-auto mb-4"
          >
            ✨ Simple Process
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="font-playfair text-white"
            style={{ fontSize: "clamp(32px, 4vw, 52px)", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: "16px" }}
          >
            How <span className="gradient-text">TripWise</span> Works
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ duration: 0.6, delay: 0.2 }}
            style={{ color: "rgba(255,255,255,0.5)", fontSize: "17px", maxWidth: "520px", margin: "0 auto", lineHeight: 1.7 }}
          >
            Three simple steps to your perfect trip, powered by cutting-edge AI technology
          </motion.p>
        </div>

        {/* Cards */}
        <div className="grid md:grid-cols-3 gap-8">
          {steps.map((step, i) => {
            const Icon = step.icon;
            return (
              <motion.div
                key={step.step}
                initial={{ opacity: 0, y: 50 }}
                animate={inView ? { opacity: 1, y: 0 } : {}}
                transition={{ duration: 0.7, delay: i * 0.18 }}
                className="glass-card rounded-2xl p-8 relative group"
              >
                {/* Step number watermark */}
                <div
                  className="absolute top-6 right-6 text-7xl font-black opacity-5 leading-none select-none"
                  style={{ fontFamily: "'Inter', sans-serif", color: "#fff" }}
                >
                  {step.step}
                </div>

                {/* Icon */}
                <motion.div
                  whileHover={{ scale: 1.1, rotate: 5 }}
                  className="w-16 h-16 rounded-2xl flex items-center justify-center mb-6"
                  style={{
                    background: `linear-gradient(135deg, ${step.glow.replace("0.3)", "0.2)")}, ${step.glow.replace("0.3)", "0.05)")})`,
                    border: `1px solid ${step.glow}`,
                    boxShadow: `0 0 40px ${step.glow}`,
                    transition: "all 0.3s ease",
                  }}
                >
                  <Icon size={28} color="#34d399" />
                </motion.div>

                {/* Step label */}
                <div style={{ fontSize: "11px", fontWeight: 700, color: "#10b981", letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: "12px" }}>
                  Step {step.step}
                </div>

                {/* Title */}
                <h3 className="text-white font-semibold mb-3" style={{ fontSize: "20px", letterSpacing: "-0.01em" }}>
                  {step.title}
                </h3>

                {/* Description */}
                <p style={{ color: "rgba(255,255,255,0.5)", fontSize: "14px", lineHeight: 1.75 }}>
                  {step.description}
                </p>

                {/* Bottom accent */}
                <motion.div
                  initial={{ scaleX: 0 }}
                  animate={inView ? { scaleX: 1 } : {}}
                  transition={{ duration: 0.8, delay: 0.4 + i * 0.2 }}
                  className="absolute bottom-0 left-0 right-0 h-0.5 rounded-b-2xl"
                  style={{ background: `linear-gradient(90deg, transparent, ${step.glow}, transparent)`, transformOrigin: "left" }}
                />
              </motion.div>
            );
          })}
        </div>

        {/* Connector dots */}
        <div className="hidden md:flex items-center justify-center mt-8 gap-2">
          {steps.map((_, i) => (
            <div key={i} className="flex items-center gap-2">
              <motion.div
                initial={{ scale: 0 }}
                animate={inView ? { scale: 1 } : {}}
                transition={{ delay: 0.6 + i * 0.15 }}
                className="w-2 h-2 rounded-full"
                style={{ background: "#10b981" }}
              />
              {i < steps.length - 1 && (
                <motion.div
                  initial={{ scaleX: 0 }}
                  animate={inView ? { scaleX: 1 } : {}}
                  transition={{ duration: 0.5, delay: 0.7 + i * 0.15 }}
                  className="w-20 h-px"
                  style={{ background: "linear-gradient(90deg, #10b981, #0ea5e9)", transformOrigin: "left" }}
                />
              )}
            </div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default HowItWorks;
