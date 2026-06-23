import { useState } from 'react';
import { motion } from 'framer-motion';
import { ExternalLink, Star, Phone, MapPin, Globe, Search, Filter } from 'lucide-react';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

const AGENCIES = [
  { name:"Cox & Kings", city:"Mumbai", rating:4.7, speciality:["International","Luxury","Adventure"],
    phone:"+91 22 2270 0700", website:"https://www.coxandkings.com", budget:"₹30,000+",
    description:"India's oldest travel company, founded 1758. Premium international and luxury tours.",
    logo:"https://upload.wikimedia.org/wikipedia/commons/thumb/0/0c/Cox_%26_Kings_logo.svg/200px-Cox_%26_Kings_logo.svg.png" },
  { name:"Thomas Cook India", city:"Mumbai", rating:4.6, speciality:["International","Family","Honeymoon"],
    phone:"+91 22 6160 3333", website:"https://www.thomascook.in", budget:"₹25,000+",
    description:"Global travel brand with extensive India and international packages.",
    logo:"https://upload.wikimedia.org/wikipedia/commons/4/4a/Thomas_Cook_logo.svg" },
  { name:"MakeMyTrip", city:"Gurugram", rating:4.4, speciality:["Flights","Hotels","Holidays"],
    phone:"+91 92 1119 1919", website:"https://www.makemytrip.com", budget:"₹5,000+",
    description:"India's leading online travel company — flights, hotels, and holiday packages.",
    logo:"https://imgak.mmtcdn.com/pwa_v3/pwa_hotel_assets/header/mmtLogoWhite25Nov.png" },
  { name:"Goibibo", city:"Gurugram", rating:4.3, speciality:["Flights","Hotels","Trains"],
    phone:"+91 1800 208 0808", website:"https://www.goibibo.com", budget:"₹3,000+",
    description:"Popular online booking platform for flights, hotels, trains, and holiday packages." },
  { name:"Yatra", city:"Gurugram", rating:4.2, speciality:["Flights","Hotels","Pilgrimage"],
    phone:"+91 95 5580 0800", website:"https://www.yatra.com", budget:"₹4,000+",
    description:"Online travel portal specializing in domestic and international travel bookings." },
  { name:"Kesari Tours", city:"Pune", rating:4.6, speciality:["International","Family","Group Tours"],
    phone:"+91 20 6611 7777", website:"https://www.kesari.in", budget:"₹35,000+",
    description:"One of India's top group tour operators with 40+ years of experience." },
  { name:"SOTC Travel", city:"Mumbai", rating:4.5, speciality:["International","Europe","Southeast Asia"],
    phone:"+91 22 6742 0000", website:"https://www.sotc.in", budget:"₹40,000+",
    description:"Premium international holiday packages, especially popular for European tours." },
  { name:"Club Mahindra", city:"Mumbai", rating:4.3, speciality:["Resorts","Family","Leisure"],
    phone:"+91 22 6890 0000", website:"https://www.clubmahindra.com", budget:"₹20,000+",
    description:"India's largest leisure company with 100+ resorts across India and abroad." },
  { name:"Thrillophilia", city:"Bangalore", rating:4.5, speciality:["Adventure","Trekking","Weekend Getaways"],
    phone:"+91 80 4646 4646", website:"https://www.thrillophilia.com", budget:"₹2,000+",
    description:"India's largest adventure travel platform — treks, camps, and unique experiences." },
  { name:"Holiday Tribe", city:"Gurugram", rating:4.4, speciality:["Weekend Trips","Group Travel","Young Travelers"],
    phone:"+91 98 1052 3223", website:"https://www.holidaytribe.com", budget:"₹3,500+",
    description:"Curated weekend trips and group travel packages for young Indians." },
  { name:"Veena World", city:"Mumbai", rating:4.6, speciality:["International","Europe","Seniors"],
    phone:"+91 22 6711 9500", website:"https://www.veenaworld.com", budget:"₹45,000+",
    description:"Award-winning travel company specializing in quality international tours." },
  { name:"Rayna Tours", city:"Dubai", rating:4.7, speciality:["Dubai","Middle East","Luxury"],
    phone:"+971 4 239 9500", website:"https://www.raynatours.com", budget:"₹25,000+",
    description:"Leading tour operator for Dubai and Middle East packages from India." },
  { name:"G Adventures", city:"Mumbai", rating:4.8, speciality:["Adventure","Solo Travel","Offbeat"],
    phone:"+91 22 6120 3456", website:"https://www.gadventures.com/in", budget:"₹30,000+",
    description:"Global small group adventure travel company with offbeat itineraries." },
  { name:"Pickyourtrail", city:"Chennai", rating:4.5, speciality:["Honeymoon","Customized","Luxury"],
    phone:"+91 44 4747 9999", website:"https://www.pickyourtrail.com", budget:"₹40,000+",
    description:"Customized honeymoon and leisure holiday packages with 24/7 support." },
  { name:"IndiHike", city:"Bangalore", rating:4.8, speciality:["Trekking","Himalayas","Adventure"],
    phone:"+91 80 6940 4000", website:"https://indiahikes.com", budget:"₹5,000+",
    description:"India's largest trekking company — Himalayan treks with certified trek leaders." },
  { name:"Zostel", city:"Delhi", rating:4.4, speciality:["Backpacker","Hostels","Budget Travel"],
    phone:"+91 11 4141 4141", website:"https://www.zostel.com", budget:"₹500+",
    description:"India's most popular hostel chain — budget stays and traveler community." },
  { name:"EaseMyTrip", city:"Delhi", rating:4.2, speciality:["Flights","Hotels","Buses"],
    phone:"+91 11 4444 4444", website:"https://www.easemytrip.com", budget:"₹2,000+",
    description:"Online travel platform with zero convenience fee on flight bookings." },
  { name:"Akbar Travels", city:"Mumbai", rating:4.3, speciality:["International","Hajj","Umrah","Budget"],
    phone:"+91 22 2300 2300", website:"https://www.akbartravels.com", budget:"₹15,000+",
    description:"One of India's largest travel agencies with 500+ offices nationwide." },
];

const ALL_SPECIALITIES = Array.from(new Set(AGENCIES.flatMap(a => a.speciality))).sort();

export default function Agencies() {
  const [darkMode,  setDarkMode]  = useState(true);
  const [search,    setSearch]    = useState('');
  const [filter,    setFilter]    = useState('All');

  const filtered = AGENCIES.filter(a => {
    const matchSearch = a.name.toLowerCase().includes(search.toLowerCase()) ||
                        a.city.toLowerCase().includes(search.toLowerCase()) ||
                        a.speciality.some(s => s.toLowerCase().includes(search.toLowerCase()));
    const matchFilter = filter === 'All' || a.speciality.includes(filter);
    return matchSearch && matchFilter;
  });

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-[#020817] text-white' : 'bg-gray-50 text-gray-900'}`}>
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

      <main className="flex-grow pt-28 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto w-full">

        {/* Header */}
        <motion.div initial={{ opacity:0, y:-20 }} animate={{ opacity:1, y:0 }} className="text-center mb-10">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full mb-4 text-sm font-medium"
            style={{ background:'rgba(16,185,129,0.1)', border:'1px solid rgba(16,185,129,0.25)', color:'#34d399' }}>
            <Globe size={14} /> Top Travel Agencies in India
          </div>
          <h1 className="font-playfair text-4xl sm:text-5xl font-bold mb-3">Travel Agencies</h1>
          <p className={`text-base max-w-md mx-auto ${darkMode?'text-white/50':'text-gray-500'}`}>
            Discover India's best travel agencies — compare packages, ratings, and contact details.
          </p>
        </motion.div>

        {/* Search + Filter */}
        <div className="flex flex-col sm:flex-row gap-3 mb-8">
          <div className="relative flex-1">
            <Search size={16} className="absolute left-4 top-1/2 -translate-y-1/2 text-white/40" />
            <input type="text" placeholder="Search agencies, cities, specialities..."
              value={search} onChange={e => setSearch(e.target.value)}
              className={`w-full pl-10 pr-4 py-3 rounded-xl text-sm outline-none transition-all ${darkMode?'text-white placeholder:text-white/30':'text-gray-900 placeholder:text-gray-400'}`}
              style={{ background: darkMode?'rgba(255,255,255,0.06)':'white', border: darkMode?'1px solid rgba(255,255,255,0.1)':'1px solid #e5e7eb' }} />
          </div>
          <div className="relative">
            <Filter size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-emerald-400" />
            <select value={filter} onChange={e => setFilter(e.target.value)}
              className={`pl-9 pr-8 py-3 rounded-xl text-sm outline-none appearance-none cursor-pointer ${darkMode?'text-white':'text-gray-900'}`}
              style={{ background: darkMode?'rgba(255,255,255,0.06)':'white', border: darkMode?'1px solid rgba(255,255,255,0.1)':'1px solid #e5e7eb' }}>
              <option value="All">All Types</option>
              {ALL_SPECIALITIES.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>
        </div>

        <p className={`text-sm mb-6 ${darkMode?'text-white/40':'text-gray-400'}`}>{filtered.length} agencies found</p>

        {/* Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-5">
          {filtered.map((agency, i) => (
            <motion.div key={agency.name}
              initial={{ opacity:0, y:20 }} animate={{ opacity:1, y:0 }} transition={{ delay: i * 0.04 }}
              className={`rounded-2xl p-5 flex flex-col gap-4 transition-all hover:-translate-y-1 hover:shadow-xl ${darkMode?'hover:shadow-emerald-500/10 hover:border-emerald-500/20':''}`}
              style={{ background: darkMode?'rgba(255,255,255,0.04)':'white', border: darkMode?'1px solid rgba(255,255,255,0.08)':'1px solid #e5e7eb', boxShadow: darkMode?'none':'0 1px 3px rgba(0,0,0,0.06)' }}>

              {/* Top */}
              <div className="flex items-start justify-between gap-3">
                <div className="flex-1">
                  <h3 className={`font-bold text-lg leading-tight mb-1 ${darkMode?'text-white':'text-gray-900'}`}>{agency.name}</h3>
                  <div className="flex items-center gap-2">
                    <MapPin size={12} className="text-emerald-400" />
                    <span className={`text-xs ${darkMode?'text-white/50':'text-gray-500'}`}>{agency.city}</span>
                  </div>
                </div>
                <div className="flex items-center gap-1 px-2 py-1 rounded-lg"
                  style={{ background: darkMode?'rgba(251,191,36,0.1)':'rgba(251,191,36,0.15)' }}>
                  <Star size={12} className="text-amber-400 fill-amber-400" />
                  <span className="text-amber-400 text-xs font-bold">{agency.rating}</span>
                </div>
              </div>

              {/* Description */}
              <p className={`text-sm leading-relaxed ${darkMode?'text-white/60':'text-gray-600'}`}>{agency.description}</p>

              {/* Tags */}
              <div className="flex flex-wrap gap-1.5">
                {agency.speciality.map(s => (
                  <span key={s} className="px-2 py-0.5 rounded-full text-xs font-medium"
                    style={{ background: darkMode?'rgba(16,185,129,0.1)':'rgba(16,185,129,0.08)', color:'#34d399', border:'1px solid rgba(16,185,129,0.2)' }}>
                    {s}
                  </span>
                ))}
              </div>

              {/* Budget */}
              <div className={`flex items-center justify-between text-sm ${darkMode?'text-white/50':'text-gray-500'}`}>
                <span>Starting from <span className="font-semibold text-emerald-400">{agency.budget}</span></span>
              </div>

              {/* Actions */}
              <div className="flex gap-2 mt-auto">
                {agency.phone && (
                  <a href={`tel:${agency.phone}`}
                    className={`flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium transition-colors flex-1 justify-center ${darkMode?'bg-white/5 text-white/70 hover:bg-white/10 hover:text-white border border-white/10':'bg-gray-50 text-gray-600 hover:bg-gray-100 border border-gray-200'}`}>
                    <Phone size={12} /> Call
                  </a>
                )}
                <a href={agency.website} target="_blank" rel="noopener noreferrer"
                  className="flex items-center gap-1.5 px-3 py-2 rounded-xl text-xs font-medium text-white transition-all flex-1 justify-center"
                  style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                  <ExternalLink size={12} /> Visit Website
                </a>
              </div>
            </motion.div>
          ))}
        </div>

        {filtered.length === 0 && (
          <div className="text-center py-20">
            <p className={`text-lg ${darkMode?'text-white/40':'text-gray-400'}`}>No agencies found for "{search}"</p>
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}
