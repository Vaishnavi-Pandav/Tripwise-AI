import { useState } from "react";
import Navbar from "../components/Navbar";
import HeroSection from "../components/HeroSection";
import StatsSection from "../components/StatsSection";
import HowItWorks from "../components/HowItWorks";
import DestinationsSection from "../components/DestinationsSection";
import AIFeaturesSection from "../components/AIFeaturesSection";
import WhyChooseUs from "../components/WhyChooseUs";
import PackagesSection from "../components/PackagesSection";
import ChatShowcase from "../components/ChatShowcase";
import TestimonialsSection from "../components/TestimonialsSection";
import BlogSection from "../components/BlogSection";
import CTASection from "../components/CTASection";
import Footer from "../components/Footer";

const Home = () => {
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div
      className="min-h-screen"
      style={{
        background: darkMode
          ? "linear-gradient(180deg, #020817 0%, #0a1628 50%, #020817 100%)"
          : "linear-gradient(180deg, #0f172a 0%, #0a1628 50%, #0f172a 100%)",
      }}
    >
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
      <main>
        <HeroSection />
        <StatsSection />
        <HowItWorks />
        <DestinationsSection />
        <AIFeaturesSection />
        <WhyChooseUs />
        <PackagesSection />
        <ChatShowcase />
        <TestimonialsSection />
        <BlogSection />
        <CTASection />
      </main>
      <Footer />
    </div>
  );
};

export default Home;