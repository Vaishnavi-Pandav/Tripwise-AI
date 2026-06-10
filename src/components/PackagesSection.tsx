import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { MapPin, Star, Clock, Wifi, UtensilsCrossed, Car, ArrowRight } from "lucide-react";

const packages = [
  {
    id: "goa-beach",
    name: "Goa Beach Escape",
    location: "Goa, India",
    image: "/goa.png",
    price: "₹12,499",
    duration: "5 Days / 4 Nights",
    rating: 4.8,
    reviews: 324,
    tag: "Best Seller",
    tagColor: "#10b981",
    services: ["Hotel", "Meals", "Transport", "WiFi"],
    description: "Sun-soaked beaches, vibrant nightlife, and coastal Goan cuisine in an all-inclusive package.",
  },
  {
    id: "himalayan-adventure",
    name: "Himalayan Adventure",
    location: "Manali, India",
    image: "/manali.png",
    price: "₹18,999",
    duration: "7 Days / 6 Nights",
    rating: 4.9,
    reviews: 198,
    tag: "Adventure",
    tagColor: "#0ea5e9",
    services: ["Hotel", "Meals", "Transport", "Guide"],
    description: "Trek through snow-capped peaks, explore ancient monasteries, and experience Himalayan culture.",
  },
  {
    id: "dubai-luxury",
    name: "Dubai Luxury Tour",
    location: "Dubai, UAE",
    image: "/dubai.png",
    price: "₹89,999",
    duration: "6 Days / 5 Nights",
    rating: 4.9,
    reviews: 156,
    tag: "Luxury",
    tagColor: "#f59e0b",
    services: ["Hotel", "Meals", "Transport", "WiFi"],
    description: "5-star hotels, Burj Khalifa visits, desert safaris, and the finest dining in the world.",
  },
  {
    id: "bali-relaxation",
    name: "Bali Relaxation Package",
    location: "Bali, Indonesia",
    image: "/bali.png",
    price: "₹54,999",
    duration: "8 Days / 7 Nights",
    rating: 4.8,
    reviews: 287,
    tag: "Most Popular",
    tagColor: "#8b5cf6",
    services: ["Villa", "Meals", "Transport", "Spa"],
    description: "Infinity pool villas, yoga retreats, temple visits, and traditional Balinese healing ceremonies.",
  },
];

const serviceIcons: Record<string, React.ReactNode> = {
  Hotel: <Wifi size={12} />,
  Villa: <Wifi size={12} />,
  Meals: <UtensilsCrossed size={12} />,
  Transport: <Car size={12} />,
  WiFi: <Wifi size={12} />,
  Guide: <Star size={12} />,
  Spa: <Star size={12} />,
};

const PackagesSection = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section id="packages" ref={ref} className="relative section-padding" style={{ padding: "100px 0", background: "rgba(10,22,40,0.4)" }}>
      <div className="container-custom">
        {/* Header */}
        <div className="text-center mb-14">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            className="section-badge mx-auto mb-4"
          >
            🎁 Travel Packages
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            animate={inView ? { opacity: 1, y: 0 } : {}}
            transition={{ delay: 0.1 }}
            className="font-playfair text-white"
            style={{ fontSize: "clamp(30px, 4vw, 52px)", fontWeight: 700, letterSpacing: "-0.02em", marginBottom: "16px" }}
          >
            Featured <span className="gradient-text">Travel Packages</span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.2 }}
            style={{ color: "rgba(255,255,255,0.5)", fontSize: "16px", maxWidth: "480px", margin: "0 auto" }}
          >
            Curated packages with everything included — accommodation, meals, transport, and experiences
          </motion.p>
        </div>

        {/* Package cards */}
        <div className="grid md:grid-cols-2 xl:grid-cols-4 gap-6">
          {packages.map((pkg, i) => (
            <motion.div
              key={pkg.id}
              initial={{ opacity: 0, y: 50 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.65, delay: i * 0.12 }}
              className="package-card"
              style={{
                background: "rgba(255,255,255,0.04)",
                border: "1px solid rgba(255,255,255,0.08)",
              }}
            >
              {/* Image */}
              <div className="relative h-48 overflow-hidden">
                <img
                  src={pkg.image}
                  alt={`${pkg.name} travel package`}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(2,8,23,0.6), transparent)" }} />
                {/* Tag */}
                <div
                  className="absolute top-3 left-3 text-xs font-bold px-2.5 py-1 rounded-full"
                  style={{ background: `${pkg.tagColor}25`, border: `1px solid ${pkg.tagColor}55`, color: pkg.tagColor, backdropFilter: "blur(8px)" }}
                >
                  {pkg.tag}
                </div>
                {/* Duration */}
                <div
                  className="absolute bottom-3 right-3 flex items-center gap-1 text-xs text-white px-2 py-1 rounded-full"
                  style={{ background: "rgba(0,0,0,0.5)", backdropFilter: "blur(8px)" }}
                >
                  <Clock size={10} />
                  {pkg.duration}
                </div>
              </div>

              {/* Content */}
              <div className="p-5">
                <div className="flex items-center gap-1.5 mb-2">
                  <MapPin size={12} color="#10b981" />
                  <span style={{ color: "rgba(255,255,255,0.5)", fontSize: "12px" }}>{pkg.location}</span>
                </div>
                <h3 className="text-white font-bold mb-2" style={{ fontSize: "17px", letterSpacing: "-0.01em" }}>
                  {pkg.name}
                </h3>
                <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "12px", lineHeight: 1.65, marginBottom: "14px" }}>
                  {pkg.description}
                </p>

                {/* Services */}
                <div className="flex flex-wrap gap-2 mb-4">
                  {pkg.services.map((s) => (
                    <div
                      key={s}
                      className="flex items-center gap-1 px-2 py-1 rounded-lg text-xs font-medium"
                      style={{
                        background: "rgba(16,185,129,0.08)",
                        border: "1px solid rgba(16,185,129,0.2)",
                        color: "#34d399",
                      }}
                    >
                      {serviceIcons[s] || null}
                      {s}
                    </div>
                  ))}
                </div>

                {/* Price + rating + CTA */}
                <div className="flex items-center gap-1 mb-4">
                  {[...Array(5)].map((_, j) => (
                    <Star
                      key={j}
                      size={12}
                      color={j < Math.floor(pkg.rating) ? "#f59e0b" : "rgba(255,255,255,0.2)"}
                      fill={j < Math.floor(pkg.rating) ? "#f59e0b" : "none"}
                    />
                  ))}
                  <span style={{ color: "rgba(255,255,255,0.5)", fontSize: "12px", marginLeft: "4px" }}>
                    {pkg.rating} ({pkg.reviews})
                  </span>
                </div>

                <div className="flex items-center justify-between">
                  <div>
                    <div style={{ color: "rgba(255,255,255,0.4)", fontSize: "11px" }}>Starting from</div>
                    <div className="gradient-text font-black text-xl">{pkg.price}</div>
                  </div>
                  <motion.button
                    whileHover={{ scale: 1.05 }}
                    whileTap={{ scale: 0.95 }}
                    id={`view-${pkg.id}-btn`}
                    className="flex items-center gap-1.5 px-4 py-2 rounded-xl text-sm font-semibold"
                    style={{
                      background: "linear-gradient(135deg, #10b981, #0ea5e9)",
                      color: "white",
                      border: "none",
                      cursor: "pointer",
                    }}
                  >
                    View
                    <ArrowRight size={13} />
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

export default PackagesSection;
