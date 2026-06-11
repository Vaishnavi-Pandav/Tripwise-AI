import { useRef } from "react";
import { motion, useInView } from "framer-motion";
import { Clock, ArrowRight } from "lucide-react";

const posts = [
  {
    id: "budget-tips",
    title: "10 Budget Travel Hacks That Actually Work in 2025",
    excerpt:
      "Discover how to cut your travel costs by 40% without sacrificing any of the experience. From flight timing strategies to hidden hotel deals.",
    category: "Budget Travel",
    readTime: "8 min read",
    date: "Jun 8, 2026",
    color: "#10b981",
    image: "https://images.unsplash.com/photo-1436491865332-7a61a109cc05?w=600&auto=format&fit=crop",
    emoji: "💰",
  },
  {
    id: "hidden-india",
    title: "India's Best Hidden Destinations Most Tourists Miss",
    excerpt:
      "From the surreal lakes of Spiti Valley to the mystical caves of Meghalaya — explore India's jaw-dropping destinations that remain crowd-free.",
    category: "Hidden Gems",
    readTime: "11 min read",
    date: "Jun 5, 2026",
    color: "#8b5cf6",
    image: "https://images.unsplash.com/photo-1524492412937-b28074a5d7da?w=600&auto=format&fit=crop",
    emoji: "🗺️",
  },
  {
    id: "ai-planning",
    title: "How AI is Revolutionizing the Way We Plan Travel",
    excerpt:
      "From personalized itineraries to predictive pricing, explore how artificial intelligence is making travel smarter, cheaper, and more meaningful.",
    category: "AI & Tech",
    readTime: "6 min read",
    date: "Jun 1, 2026",
    color: "#0ea5e9",
    image: "https://images.unsplash.com/photo-1483683804023-6ccdb62f86ef?w=600&auto=format&fit=crop",
    emoji: "🤖",
  },
];

const BlogSection = () => {
  const ref = useRef<HTMLElement>(null);
  const inView = useInView(ref, { once: true, margin: "-80px" });

  return (
    <section ref={ref} className="relative section-padding" style={{ padding: "100px 0" }}>
      <div className="container-custom">
        {/* Header */}
        <div className="flex items-end justify-between mb-14 flex-wrap gap-4">
          <div>
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              className="section-badge mb-4"
            >
              📖 Travel Blog
            </motion.div>
            <motion.h2
              initial={{ opacity: 0, y: 20 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ delay: 0.1 }}
              className="font-playfair text-white"
              style={{ fontSize: "clamp(28px, 4vw, 48px)", fontWeight: 700, letterSpacing: "-0.02em" }}
            >
              Travel <span className="gradient-text">Insights & Tips</span>
            </motion.h2>
          </div>
          <motion.button
            initial={{ opacity: 0 }}
            animate={inView ? { opacity: 1 } : {}}
            transition={{ delay: 0.3 }}
            whileHover={{ scale: 1.05 }}
            className="btn-outline flex items-center gap-2"
            style={{ padding: "10px 24px", fontSize: "14px" }}
          >
            View All Posts
            <ArrowRight size={15} />
          </motion.button>
        </div>

        {/* Cards */}
        <div className="grid md:grid-cols-3 gap-6">
          {posts.map((post, i) => (
            <motion.article
              key={post.id}
              initial={{ opacity: 0, y: 40 }}
              animate={inView ? { opacity: 1, y: 0 } : {}}
              transition={{ duration: 0.65, delay: i * 0.12 }}
              className="glass-card rounded-2xl overflow-hidden group cursor-pointer"
            >
              {/* Image */}
              <div className="relative h-48 overflow-hidden">
                <img
                  src={post.image}
                  alt={post.title}
                  className="w-full h-full object-cover transition-transform duration-500 group-hover:scale-105"
                />
                <div className="absolute inset-0" style={{ background: "linear-gradient(to top, rgba(2,8,23,0.7), transparent)" }} />
                {/* Category tag */}
                <div
                  className="absolute top-4 left-4 px-3 py-1.5 rounded-full text-xs font-bold"
                  style={{ background: `${post.color}25`, border: `1px solid ${post.color}55`, color: post.color, backdropFilter: "blur(8px)" }}
                >
                  {post.emoji} {post.category}
                </div>
              </div>

              {/* Content */}
              <div className="p-6">
                <div className="flex items-center gap-3 mb-3" style={{ color: "rgba(255,255,255,0.35)", fontSize: "12px" }}>
                  <span>{post.date}</span>
                  <span>·</span>
                  <span className="flex items-center gap-1">
                    <Clock size={11} />
                    {post.readTime}
                  </span>
                </div>
                <h3 className="text-white font-bold mb-3" style={{ fontSize: "17px", lineHeight: 1.4, letterSpacing: "-0.01em" }}>
                  {post.title}
                </h3>
                <p style={{ color: "rgba(255,255,255,0.45)", fontSize: "13px", lineHeight: 1.75, marginBottom: "20px" }}>
                  {post.excerpt}
                </p>
                <div
                  className="flex items-center gap-2 text-sm font-semibold transition-all duration-300 group-hover:gap-3"
                  style={{ color: post.color }}
                >
                  Read More
                  <ArrowRight size={14} />
                </div>
              </div>
            </motion.article>
          ))}
        </div>
      </div>
    </section>
  );
};

export default BlogSection;
