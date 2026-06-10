import React, { useState } from 'react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import { motion } from 'framer-motion';
import { Star, MapPin, Calendar, DollarSign, Filter, Search } from 'lucide-react';

const MOCK_DESTINATIONS = [
  {
    id: '1',
    name: 'Santorini, Greece',
    image: 'https://images.unsplash.com/photo-1613395877344-13d4a8e0d49e?auto=format&fit=crop&w=800&q=80',
    budget: '$1500 - $3000',
    rating: 4.9,
    season: 'May - Sep',
    description: 'Iconic white-washed buildings, stunning sunsets, and crystal clear Aegean waters.',
    type: 'Beach',
  },
  {
    id: '2',
    name: 'Kyoto, Japan',
    image: 'https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=800&q=80',
    budget: '$1200 - $2500',
    rating: 4.8,
    season: 'Mar - May',
    description: 'Experience traditional temples, serene gardens, and beautiful cherry blossoms.',
    type: 'Cultural',
  },
  {
    id: '3',
    name: 'Banff, Canada',
    image: 'https://images.unsplash.com/photo-1521404169724-699e190ebf9e?auto=format&fit=crop&w=800&q=80',
    budget: '$1000 - $2200',
    rating: 4.7,
    season: 'Jun - Aug',
    description: 'Majestic mountain peaks, turquoise glacial lakes, and abundant wildlife.',
    type: 'Mountain',
  },
  {
    id: '4',
    name: 'Amalfi Coast, Italy',
    image: 'https://images.unsplash.com/photo-1533676802871-eca1ae998cd5?auto=format&fit=crop&w=800&q=80',
    budget: '$2000 - $4000',
    rating: 4.9,
    season: 'May - Oct',
    description: 'Dramatic coastlines, colorful cliffside villages, and incredible Italian cuisine.',
    type: 'Coastal',
  },
  {
    id: '5',
    name: 'Bali, Indonesia',
    image: 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=800&q=80',
    budget: '$800 - $1500',
    rating: 4.6,
    season: 'Apr - Oct',
    description: 'Lush rice terraces, ancient temples, and vibrant cultural retreats.',
    type: 'Tropical',
  },
  {
    id: '6',
    name: 'Swiss Alps, Switzerland',
    image: 'https://images.unsplash.com/photo-1531366936337-7c912a458b1c?auto=format&fit=crop&w=800&q=80',
    budget: '$2500 - $5000',
    rating: 4.9,
    season: 'Dec - Mar',
    description: 'World-class skiing, picturesque alpine villages, and breathtaking scenery.',
    type: 'Winter',
  }
];

const Results = () => {
  const [darkMode, setDarkMode] = useState(true);

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-[#020817] text-white' : 'bg-gray-50 text-gray-900'}`}>
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />
      
      <main className="flex-grow pt-24 pb-12 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">
        
        {/* Search Summary Header */}
        <motion.div 
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className={`p-6 rounded-2xl mb-8 border ${darkMode ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200 shadow-sm'}`}
        >
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <div>
              <h1 className="text-2xl font-playfair font-bold mb-2">
                We found <span className="text-emerald-400">12</span> destinations for your dream trip
              </h1>
              <div className="flex flex-wrap gap-3 text-sm opacity-70">
                <span className="flex items-center gap-1"><MapPin size={14} /> Europe</span>
                <span className="flex items-center gap-1"><Calendar size={14} /> 7 Days</span>
                <span className="flex items-center gap-1"><DollarSign size={14} /> $2000 - $3000</span>
              </div>
            </div>
            <button className={`px-4 py-2 rounded-full flex items-center gap-2 text-sm font-medium transition-colors ${darkMode ? 'bg-white/10 hover:bg-white/20' : 'bg-gray-100 hover:bg-gray-200'}`}>
              <Search size={16} /> Edit Search
            </button>
          </div>
        </motion.div>

        <div className="flex flex-col lg:flex-row gap-8">
          
          {/* Sidebar Filters */}
          <aside className="w-full lg:w-64 flex-shrink-0">
            <div className={`p-6 rounded-2xl sticky top-28 border ${darkMode ? 'bg-white/5 border-white/10' : 'bg-white border-gray-200 shadow-sm'}`}>
              <div className="flex items-center gap-2 mb-6 pb-4 border-b border-white/10">
                <Filter size={18} className="text-emerald-400" />
                <h2 className="font-semibold text-lg">Filters</h2>
              </div>
              
              <div className="space-y-6">
                {/* Budget */}
                <div>
                  <h3 className="text-sm font-medium mb-3 opacity-80 uppercase tracking-wider">Budget Range</h3>
                  <div className="space-y-2">
                    {['Under $1000', '$1000 - $2000', '$2000 - $4000', '$4000+'].map((range) => (
                      <label key={range} className="flex items-center gap-3 cursor-pointer group">
                        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${darkMode ? 'border-white/30 group-hover:border-emerald-400' : 'border-gray-300 group-hover:border-emerald-500'}`}></div>
                        <span className="text-sm opacity-80 group-hover:opacity-100">{range}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Duration */}
                <div>
                  <h3 className="text-sm font-medium mb-3 opacity-80 uppercase tracking-wider">Trip Duration</h3>
                  <div className="space-y-2">
                    {['1-3 Days', '4-7 Days', '1-2 Weeks', '2+ Weeks'].map((duration) => (
                      <label key={duration} className="flex items-center gap-3 cursor-pointer group">
                        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${darkMode ? 'border-white/30 group-hover:border-emerald-400' : 'border-gray-300 group-hover:border-emerald-500'}`}></div>
                        <span className="text-sm opacity-80 group-hover:opacity-100">{duration}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Type */}
                <div>
                  <h3 className="text-sm font-medium mb-3 opacity-80 uppercase tracking-wider">Destination Type</h3>
                  <div className="space-y-2">
                    {['Beach', 'Mountain', 'City', 'Cultural'].map((type) => (
                      <label key={type} className="flex items-center gap-3 cursor-pointer group">
                        <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${darkMode ? 'border-white/30 group-hover:border-emerald-400' : 'border-gray-300 group-hover:border-emerald-500'}`}></div>
                        <span className="text-sm opacity-80 group-hover:opacity-100">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </aside>

          {/* Results Grid */}
          <div className="flex-1 grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
            {MOCK_DESTINATIONS.map((dest, index) => (
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                key={dest.id}
                className={`group rounded-2xl overflow-hidden border transition-all duration-300 hover:-translate-y-1 hover:shadow-xl ${
                  darkMode ? 'bg-white/5 border-white/10 hover:shadow-emerald-500/10 hover:border-emerald-500/30' : 'bg-white border-gray-200 shadow-sm hover:shadow-emerald-500/10 hover:border-emerald-500/30'
                }`}
              >
                {/* Card Image Header */}
                <div className="relative h-48 overflow-hidden">
                  <div className="absolute inset-0 bg-black/20 group-hover:bg-transparent transition-colors z-10" />
                  <img 
                    src={dest.image} 
                    alt={dest.name} 
                    className="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110"
                  />
                  <div className="absolute top-3 right-3 z-20 flex items-center gap-1 bg-black/50 backdrop-blur-md px-2.5 py-1 rounded-full text-white text-xs font-semibold">
                    <Star size={12} className="text-amber-400 fill-amber-400" />
                    {dest.rating}
                  </div>
                  <div className="absolute top-3 left-3 z-20 bg-emerald-500/90 backdrop-blur-md px-2.5 py-1 rounded-full text-white text-xs font-medium">
                    {dest.type}
                  </div>
                </div>

                {/* Card Content */}
                <div className="p-5">
                  <h3 className="text-xl font-bold mb-1 font-playfair">{dest.name}</h3>
                  <p className={`text-sm mb-4 line-clamp-2 ${darkMode ? 'text-white/60' : 'text-gray-600'}`}>
                    {dest.description}
                  </p>
                  
                  <div className="space-y-2 mb-6">
                    <div className="flex items-center gap-2 text-sm">
                      <DollarSign size={14} className="text-emerald-400" />
                      <span className={darkMode ? 'text-white/80' : 'text-gray-700'}>{dest.budget} <span className="text-xs opacity-60">est. total</span></span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Calendar size={14} className="text-blue-400" />
                      <span className={darkMode ? 'text-white/80' : 'text-gray-700'}>Best time: {dest.season}</span>
                    </div>
                  </div>

                  <button className="w-full py-2.5 rounded-xl bg-gradient-to-r from-emerald-500 to-emerald-400 hover:from-emerald-400 hover:to-emerald-300 text-white font-medium text-sm transition-all shadow-md shadow-emerald-500/20 active:scale-[0.98]">
                    Explore Destination
                  </button>
                </div>
              </motion.div>
            ))}
          </div>

        </div>
      </main>
      
      <Footer />
    </div>
  );
};

export default Results;
