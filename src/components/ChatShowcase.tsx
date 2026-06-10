import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Bot, User, Hotel, DollarSign, MapPin, Send } from "lucide-react";

const ChatShowcase = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  const chatMessages = [
    {
      type: "user",
      text: "Plan a 4-day Goa trip under ₹15,000 for 2 people 🏖️",
    },
    {
      type: "ai",
      isStructured: true,
    },
  ];

  return (
    <section ref={ref} className="relative section-padding" style={{ padding: "100px 0", overflow: "hidden" }}>
      {/* Gradient background */}
      <div
        className="absolute inset-0"
        style={{ background: "linear-gradient(135deg, rgba(2,8,23,0.98) 0%, rgba(10,22,40,0.9) 50%, rgba(2,8,23,0.98) 100%)" }}
      />
      <div className="orb orb-emerald absolute w-96 h-96 -top-20 right-10 opacity-15" />
      <div className="orb orb-blue absolute w-72 h-72 bottom-0 left-20 opacity-15" />

      <div className="container-custom relative z-10">
        <div className="grid lg:grid-cols-2 gap-16 items-center">
          {/* Left: Heading */}
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              className="section-badge mb-4"
            >
              💬 AI Assistant
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.1 }}
              className="font-playfair text-white mb-5"
              style={{ fontSize: "clamp(28px, 3.5vw, 48px)", fontWeight: 700, letterSpacing: "-0.02em" }}
            >
              Meet Your AI <span className="gradient-text">Travel Assistant</span>
            </motion.h2>
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.2 }}
              style={{ color: "rgba(255,255,255,0.5)", fontSize: "16px", lineHeight: 1.8, marginBottom: "32px" }}
            >
              Just describe your dream trip in plain language. Our AI understands 
              context, budget constraints, and personal preferences to build the 
              perfect itinerary in seconds.
            </motion.p>

            {/* Capability pills */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={inView ? { opacity: 1 } : {}}
              transition={{ delay: 0.35 }}
              className="flex flex-wrap gap-3"
            >
              {["Day-wise Itineraries", "Budget Breakdowns", "Hotel Suggestions", "Local Attractions", "Food Recommendations"].map((cap) => (
                <div
                  key={cap}
                  className="px-3 py-1.5 rounded-full text-sm"
                  style={{
                    background: "rgba(16,185,129,0.08)",
                    border: "1px solid rgba(16,185,129,0.25)",
                    color: "rgba(255,255,255,0.7)",
                  }}
                >
                  ✓ {cap}
                </div>
              ))}
            </motion.div>
          </div>

          {/* Right: Chat mockup */}
          <motion.div
            initial={{ opacity: 0, x: 50, scale: 0.97 }}
            animate={inView ? { opacity: 1, x: 0, scale: 1 } : {}}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div
              className="rounded-3xl overflow-hidden"
              style={{
                background: "rgba(255,255,255,0.03)",
                border: "1px solid rgba(255,255,255,0.1)",
                boxShadow: "0 40px 100px rgba(0,0,0,0.5)",
              }}
            >
              {/* Chat header */}
              <div
                className="flex items-center gap-3 px-6 py-4"
                style={{ borderBottom: "1px solid rgba(255,255,255,0.08)", background: "rgba(255,255,255,0.02)" }}
              >
                <div
                  className="w-10 h-10 rounded-full flex items-center justify-center"
                  style={{ background: "linear-gradient(135deg, #10b981, #0ea5e9)" }}
                >
                  <Bot size={18} color="white" />
                </div>
                <div>
                  <div className="text-white font-semibold text-sm">TripWise AI</div>
                  <div className="flex items-center gap-1.5 text-xs" style={{ color: "#10b981" }}>
                    <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse inline-block" />
                    Online · Responds instantly
                  </div>
                </div>
              </div>

              {/* Chat body */}
              <div className="p-6 space-y-5">
                {/* User message */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={inView ? { opacity: 1, y: 0 } : {}}
                  transition={{ delay: 0.5 }}
                  className="flex gap-3 justify-end"
                >
                  <div
                    className="chat-user px-4 py-3 max-w-xs"
                    style={{ fontSize: "14px", color: "white", lineHeight: 1.6 }}
                  >
                    {chatMessages[0].text}
                  </div>
                  <div
                    className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center"
                    style={{ background: "rgba(255,255,255,0.1)" }}
                  >
                    <User size={14} color="white" />
                  </div>
                </motion.div>

                {/* AI response */}
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={inView ? { opacity: 1, y: 0 } : {}}
                  transition={{ delay: 0.8 }}
                  className="flex gap-3"
                >
                  <div
                    className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-1"
                    style={{ background: "linear-gradient(135deg, #10b981, #0ea5e9)" }}
                  >
                    <Bot size={14} color="white" />
                  </div>
                  <div className="chat-ai px-4 py-4 flex-1" style={{ fontSize: "13px" }}>
                    <div className="text-emerald-400 font-bold text-sm mb-3">✈️ Goa Trip Plan — 4 Days | ₹14,200 est.</div>
                    
                    {/* Days */}
                    <div className="space-y-2 mb-4">
                      {[
                        { day: "Day 1", activity: "Arrive → Calangute Beach → Baga Nightlife" },
                        { day: "Day 2", activity: "North Goa: Fort Aguada → Anjuna Flea Market" },
                        { day: "Day 3", activity: "South Goa: Colva Beach → Old Goa Churches" },
                        { day: "Day 4", activity: "Water Sports → Spice Plantation → Depart" },
                      ].map((d) => (
                        <div key={d.day} className="flex gap-2" style={{ color: "rgba(255,255,255,0.75)" }}>
                          <span className="font-bold text-emerald-400 flex-shrink-0" style={{ minWidth: "50px" }}>{d.day}</span>
                          <span style={{ fontSize: "12px", lineHeight: 1.5 }}>{d.activity}</span>
                        </div>
                      ))}
                    </div>

                    {/* Info pills */}
                    <div className="grid grid-cols-2 gap-2">
                      <div className="flex items-center gap-2 px-3 py-2 rounded-xl" style={{ background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)" }}>
                        <Hotel size={12} color="#10b981" />
                        <span style={{ color: "rgba(255,255,255,0.6)", fontSize: "11px" }}>Hotel Calangute 3★</span>
                      </div>
                      <div className="flex items-center gap-2 px-3 py-2 rounded-xl" style={{ background: "rgba(14,165,233,0.1)", border: "1px solid rgba(14,165,233,0.2)" }}>
                        <DollarSign size={12} color="#0ea5e9" />
                        <span style={{ color: "rgba(255,255,255,0.6)", fontSize: "11px" }}>₹7,100 / person</span>
                      </div>
                      <div className="flex items-center gap-2 px-3 py-2 rounded-xl col-span-2" style={{ background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.2)" }}>
                        <MapPin size={12} color="#f59e0b" />
                        <span style={{ color: "rgba(255,255,255,0.6)", fontSize: "11px" }}>6 attractions · 4 restaurants · 2 adventure activities included</span>
                      </div>
                    </div>
                  </div>
                </motion.div>
              </div>

              {/* Input bar */}
              <div
                className="px-6 py-4 flex gap-3 items-center"
                style={{ borderTop: "1px solid rgba(255,255,255,0.08)" }}
              >
                <input
                  type="text"
                  placeholder="Ask me anything about your trip..."
                  className="flex-1 bg-transparent text-white/60 text-sm outline-none border-none placeholder:text-white/30"
                  readOnly
                />
                <motion.button
                  whileHover={{ scale: 1.1 }}
                  whileTap={{ scale: 0.9 }}
                  id="ai-chat-send-btn"
                  className="w-9 h-9 rounded-xl flex items-center justify-center"
                  style={{ background: "linear-gradient(135deg, #10b981, #0ea5e9)", border: "none", cursor: "pointer" }}
                >
                  <Send size={15} color="white" />
                </motion.button>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
};

export default ChatShowcase;
