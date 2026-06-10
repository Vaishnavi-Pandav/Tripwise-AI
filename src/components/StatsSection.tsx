import { useEffect, useRef, useState } from "react";
import { motion, useInView } from "framer-motion";

const stats = [
  { value: 10000, suffix: "+", label: "Trips Planned", icon: "✈️" },
  { value: 95, suffix: "%", label: "Budget Accuracy", icon: "🎯" },
  { value: 500, suffix: "+", label: "Destinations", icon: "🌍" },
  { value: 50000, suffix: "+", label: "Happy Travelers", icon: "😊" },
];

function CountUp({ target, suffix }: { target: number; suffix: string }) {
  const [count, setCount] = useState(0);
  const ref = useRef<HTMLSpanElement>(null);
  const inView = useInView(ref, { once: true, margin: "-100px" });

  useEffect(() => {
    if (!inView) return;
    let start = 0;
    const end = target;
    const duration = 2000;
    const stepTime = 20;
    const steps = duration / stepTime;
    const increment = end / steps;

    const timer = setInterval(() => {
      start += increment;
      if (start >= end) {
        setCount(end);
        clearInterval(timer);
      } else {
        setCount(Math.floor(start));
      }
    }, stepTime);
    return () => clearInterval(timer);
  }, [inView, target]);

  return (
    <span ref={ref}>
      {count.toLocaleString()}{suffix}
    </span>
  );
}

const StatsSection = () => {
  const sectionRef = useRef<HTMLElement>(null);
  const inView = useInView(sectionRef, { once: true, margin: "-80px" });

  return (
    <section ref={sectionRef} className="relative section-padding" style={{ padding: "80px 0", overflow: "hidden" }}>
      {/* Background gradient */}
      <div className="absolute inset-0" style={{
        background: "linear-gradient(180deg, rgba(2,8,23,1) 0%, rgba(10,22,40,0.8) 50%, rgba(2,8,23,1) 100%)"
      }} />

      {/* Animated decorative line */}
      <motion.div
        initial={{ scaleX: 0 }}
        animate={inView ? { scaleX: 1 } : {}}
        transition={{ duration: 1.5, ease: "easeInOut" }}
        className="absolute top-0 left-0 right-0 h-px"
        style={{ background: "linear-gradient(90deg, transparent, #10b981, #0ea5e9, transparent)", transformOrigin: "left" }}
      />
      <motion.div
        initial={{ scaleX: 0 }}
        animate={inView ? { scaleX: 1 } : {}}
        transition={{ duration: 1.5, ease: "easeInOut", delay: 0.2 }}
        className="absolute bottom-0 left-0 right-0 h-px"
        style={{ background: "linear-gradient(90deg, transparent, #a78bfa, #10b981, transparent)", transformOrigin: "right" }}
      />

      <div className="container-custom relative z-10">
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
          {stats.map((stat, i) => (
            <motion.div
              key={stat.label}
              initial={{ opacity: 0, y: 40 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.7, delay: i * 0.15 }}
              className="flex flex-col items-center text-center group"
            >
              {/* Icon bubble */}
              <motion.div
                whileHover={{ scale: 1.15, rotate: 10 }}
                className="w-16 h-16 rounded-2xl flex items-center justify-center mb-5 text-3xl"
                style={{
                  background: "rgba(255,255,255,0.04)",
                  border: "1px solid rgba(255,255,255,0.1)",
                  boxShadow: "0 8px 32px rgba(0,0,0,0.3)",
                  transition: "border-color 0.3s",
                }}
              >
                {stat.icon}
              </motion.div>

              {/* Number */}
              <div className="stat-number gradient-text mb-2" style={{ fontFamily: "'Inter', sans-serif" }}>
                <CountUp target={stat.value} suffix={stat.suffix} />
              </div>

              {/* Label */}
              <p style={{ color: "rgba(255,255,255,0.55)", fontSize: "14px", fontWeight: 500, letterSpacing: "0.025em" }}>
                {stat.label}
              </p>
            </motion.div>
          ))}
        </div>
      </div>
    </section>
  );
};

export default StatsSection;
