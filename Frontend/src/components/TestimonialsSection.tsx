import { useRef, useEffect, useState } from "react";
import { motion, useInView, AnimatePresence } from "framer-motion";
import { Star, ChevronLeft, ChevronRight, Quote } from "lucide-react";

const testimonials = [
  {
    id: 1,
    name: "Priya Sharma",
    role: "Solo Traveler",
    location: "Mumbai, India",
    avatar: "https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=100&h=100&fit=crop&crop=faces",
    rating: 5,
    review:
      "TripWise AI planned my solo Bali trip perfectly — from budget accommodation to hidden temples. Saved me 3 weeks of research in 2 minutes. Absolutely love it!",
    trip: "Bali, 10 Days",
  },
  {
    id: 2,
    name: "Arjun Mehta",
    role: "Family Traveler",
    location: "Delhi, India",
    avatar: "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=100&h=100&fit=crop&crop=faces",
    rating: 5,
    review:
      "Took my family of 5 to Switzerland using TripWise AI's itinerary. The budget was spot-on, and we didn't miss a single must-see attraction. Phenomenal service!",
    trip: "Switzerland, 12 Days",
  },
  {
    id: 3,
    name: "Sneha Reddy",
    role: "Honeymoon Traveler",
    location: "Bangalore, India",
    avatar: "https://images.unsplash.com/photo-1534528741775-53994a69daeb?w=100&h=100&fit=crop&crop=faces",
    rating: 5,
    review:
      "Our Dubai honeymoon was absolutely magical. TripWise AI suggested the most romantic restaurants and experiences we never would have found on our own!",
    trip: "Dubai, 8 Days",
  },
  {
    id: 4,
    name: "Rahul Kumar",
    role: "Adventure Traveler",
    location: "Pune, India",
    avatar: "https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?w=100&h=100&fit=crop&crop=faces",
    rating: 5,
    review:
      "The Himalayan trek itinerary was incredibly detailed — day-by-day activities, altitude acclimatization tips, and local guide recommendations. A true adventure companion!",
    trip: "Manali Trek, 9 Days",
  },
  {
    id: 5,
    name: "Ananya Nair",
    role: "Weekend Explorer",
    location: "Chennai, India",
    avatar: "https://images.unsplash.com/photo-1517841905240-472988babdf9?w=100&h=100&fit=crop&crop=faces",
    rating: 5,
    review:
      "I plan weekend getaways every month, and TripWise AI makes it effortless. The budget optimizer is a game-changer — always stays within my ₹10k limit!",
    trip: "Goa Weekend, 3 Days",
  },
];

const TestimonialsSection = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });
  const [current, setCurrent] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrent((prev) => (prev + 1) % testimonials.length);
    }, 4500);
    return () => clearInterval(interval);
  }, []);

  const prev = () => setCurrent((c) => (c - 1 + testimonials.length) % testimonials.length);
  const next = () => setCurrent((c) => (c + 1) % testimonials.length);

  const visible = [
    testimonials[current],
    testimonials[(current + 1) % testimonials.length],
    testimonials[(current + 2) % testimonials.length],
  ];

  return (
    <section id="reviews" ref={ref} className="relative section-padding" style={{ padding: "100px 0", background: "rgba(10,22,40,0.5)" }}>
      <div className="container-custom">
        {/* Header */}
        <div className="flex items-end justify-between mb-14 flex-wrap gap-4">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              className="section-badge mb-4"
            >
              ⭐ Testimonials
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.1 }}
              className="font-playfair text-white"
              style={{ fontSize: "clamp(28px, 4vw, 50px)", fontWeight: 700, letterSpacing: "-0.02em" }}
            >
              Travelers Love <span className="gradient-text">TripWise</span>
            </motion.h2>
          </div>
          <motion.div
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.3 }}
            className="flex gap-3"
          >
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={prev}
              id="testimonial-prev-btn"
              className="w-11 h-11 rounded-full flex items-center justify-center"
              style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)", cursor: "pointer" }}
            >
              <ChevronLeft size={18} color="white" />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={next}
              id="testimonial-next-btn"
              className="w-11 h-11 rounded-full flex items-center justify-center"
              style={{ background: "rgba(255,255,255,0.06)", border: "1px solid rgba(255,255,255,0.12)", cursor: "pointer" }}
            >
              <ChevronRight size={18} color="white" />
            </motion.button>
          </motion.div>
        </div>

        {/* Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          <AnimatePresence mode="wait">
            {visible.map((t, i) => (
              <motion.div
                key={`${t.id}-${i}`}
                initial={{ opacity: 0, y: 30, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.45, delay: i * 0.08 }}
                className="testimonial-card p-6 relative"
              >
                {/* Quote mark */}
                <div className="absolute top-4 right-5">
                  <Quote size={32} color="rgba(16,185,129,0.15)" />
                </div>

                {/* Stars */}
                <div className="flex gap-1 mb-4">
                  {[...Array(t.rating)].map((_, j) => (
                    <Star key={j} size={14} color="#f59e0b" fill="#f59e0b" />
                  ))}
                </div>

                {/* Review */}
                <p style={{ color: "rgba(255,255,255,0.65)", fontSize: "14px", lineHeight: 1.8, marginBottom: "20px" }}>
                  "{t.review}"
                </p>

                {/* Trip badge */}
                <div
                  className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium mb-5"
                  style={{
                    background: "rgba(16,185,129,0.1)",
                    border: "1px solid rgba(16,185,129,0.25)",
                    color: "#34d399",
                  }}
                >
                  ✈️ {t.trip}
                </div>

                {/* Author */}
                <div className="flex items-center gap-3">
                  <img
                    src={t.avatar}
                    alt={t.name}
                    className="w-10 h-10 rounded-full object-cover"
                    style={{ border: "2px solid rgba(16,185,129,0.4)" }}
                  />
                  <div>
                    <div className="text-white font-semibold text-sm">{t.name}</div>
                    <div style={{ color: "rgba(255,255,255,0.4)", fontSize: "12px" }}>
                      {t.role} · {t.location}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>
        </div>

        {/* Dots */}
        <div className="flex justify-center gap-2 mt-8">
          {testimonials.map((_, i) => (
            <button
              key={i}
              onClick={() => setCurrent(i)}
              className="rounded-full transition-all duration-300 border-none cursor-pointer"
              style={{
                width: i === current ? "24px" : "8px",
                height: "8px",
                background: i === current ? "linear-gradient(90deg, #10b981, #0ea5e9)" : "rgba(255,255,255,0.2)",
              }}
              aria-label={`Go to testimonial ${i + 1}`}
            />
          ))}
        </div>
      </div>
    </section>
  );
};

export default TestimonialsSection;
