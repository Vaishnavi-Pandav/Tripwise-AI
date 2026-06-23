import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Navigation, Plane, Train, Car, Bus } from 'lucide-react';
import { getCityCoordsWithFallback } from '../utils/cityCoords';

interface RouteMapModalProps {
  isOpen:      boolean;
  onClose:     () => void;
  source:      string;
  destination: string;
  days?:       number;
  travelers?:  number;
  budget?:     number;
}

const modeIcons: Record<string, React.ReactNode> = {
  flight: <Plane  size={14} />,
  train:  <Train  size={14} />,
  car:    <Car    size={14} />,
  bus:    <Bus    size={14} />,
};

export default function RouteMapModal({
  isOpen, onClose, source, destination, days, travelers, budget,
}: RouteMapModalProps) {
  const [mapReady, setMapReady] = useState(false);
  const mapId = 'tripwise-route-map';

  const srcCoords  = getCityCoordsWithFallback(source);
  const dstCoords  = getCityCoordsWithFallback(destination);

  // Center between the two points
  const centerLat = (srcCoords[0] + dstCoords[0]) / 2;
  const centerLng = (srcCoords[1] + dstCoords[1]) / 2;

  useEffect(() => {
    if (!isOpen) return;

    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css';
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }

    const timer = setTimeout(() => { initMap(); setMapReady(true); }, 200);
    return () => {
      clearTimeout(timer);
      const el = document.getElementById(mapId) as any;
      if (el) el._leaflet_id = null;
    };
  }, [isOpen]);

  const initMap = () => {
    import('leaflet').then((L) => {
      const container = document.getElementById(mapId);
      if (!container) return;
      if ((container as any)._leaflet_id) (container as any)._leaflet_id = null;

      // Auto-calculate zoom based on distance
      const latDiff = Math.abs(srcCoords[0] - dstCoords[0]);
      const lngDiff = Math.abs(srcCoords[1] - dstCoords[1]);
      const maxDiff = Math.max(latDiff, lngDiff);
      const zoom = maxDiff < 1 ? 11 : maxDiff < 3 ? 9 : maxDiff < 8 ? 7 : maxDiff < 15 ? 5 : 4;

      const map = L.map(mapId, { center: [centerLat, centerLng], zoom });

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© OpenStreetMap contributors',
        maxZoom: 18,
      }).addTo(map);

      // Source marker (green)
      const srcIcon = L.divIcon({
        html: `<div style="background:#10b981;width:36px;height:36px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.4);display:flex;align-items:center;justify-content:center;">
                 <span style="transform:rotate(45deg);font-size:14px;">🛫</span>
               </div>`,
        iconSize: [36, 36], iconAnchor: [18, 36], popupAnchor: [0, -38], className: '',
      });

      // Destination marker (blue)
      const dstIcon = L.divIcon({
        html: `<div style="background:#0ea5e9;width:36px;height:36px;border-radius:50% 50% 50% 0;transform:rotate(-45deg);border:3px solid white;box-shadow:0 2px 8px rgba(0,0,0,0.4);">
                 <span style="transform:rotate(45deg);display:block;text-align:center;font-size:14px;padding-top:4px;">📍</span>
               </div>`,
        iconSize: [36, 36], iconAnchor: [18, 36], popupAnchor: [0, -38], className: '',
      });

      // Add markers
      L.marker(srcCoords, { icon: srcIcon }).addTo(map)
        .bindPopup(`<b>🛫 From: ${source}</b><br><small>Starting point</small>`);

      L.marker(dstCoords, { icon: dstIcon }).addTo(map)
        .bindPopup(`<b>📍 To: ${destination}</b>${days ? `<br><small>${days} days${travelers ? `, ${travelers} traveler${travelers>1?'s':''}` : ''}</small>` : ''}${budget ? `<br><small>Budget: ₹${budget.toLocaleString()}</small>` : ''}`);

      // Draw dashed route line
      const routeLine = L.polyline([srcCoords, dstCoords], {
        color: '#10b981',
        weight: 3,
        opacity: 0.8,
        dashArray: '10, 8',
      }).addTo(map);

      // Fit both markers
      map.fitBounds(routeLine.getBounds(), { padding: [60, 60] });

      // Midpoint label
      const midLat = (srcCoords[0] + dstCoords[0]) / 2;
      const midLng = (srcCoords[1] + dstCoords[1]) / 2;
      const distKm = Math.round(L.latLng(srcCoords).distanceTo(L.latLng(dstCoords)) / 1000);

      L.marker([midLat, midLng], {
        icon: L.divIcon({
          html: `<div style="background:rgba(16,185,129,0.9);color:white;padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;white-space:nowrap;box-shadow:0 2px 6px rgba(0,0,0,0.3);">~${distKm.toLocaleString()} km</div>`,
          className: '', iconAnchor: [40, 12],
        }),
      }).addTo(map);
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div key="route-backdrop"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" />

          <motion.div key="route-modal"
            initial={{ opacity: 0, scale: 0.96, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 20 }}
            transition={{ duration: 0.25 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">

            <div className="w-full max-w-3xl pointer-events-auto rounded-2xl overflow-hidden flex flex-col"
              style={{ background:'rgba(2,8,23,0.98)', border:'1px solid rgba(255,255,255,0.12)',
                       boxShadow:'0 40px 80px rgba(0,0,0,0.7)', height:'560px' }}>

              {/* Header */}
              <div className="flex items-center justify-between px-5 py-4 flex-shrink-0"
                style={{ borderBottom:'1px solid rgba(255,255,255,0.08)' }}>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                    style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                    <Navigation size={16} className="text-white" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-sm">Route Map</h3>
                    <p className="text-white/40 text-xs">{source} → {destination}</p>
                  </div>
                </div>
                <button onClick={onClose}
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white/60 hover:text-white"
                  style={{ background:'rgba(255,255,255,0.08)' }}>
                  <X size={16} />
                </button>
              </div>

              {/* Route pills */}
              <div className="flex items-center gap-3 px-5 py-3 flex-shrink-0"
                style={{ borderBottom:'1px solid rgba(255,255,255,0.06)' }}>
                <span className="px-3 py-1 rounded-full text-xs font-medium text-white"
                  style={{ background:'rgba(16,185,129,0.15)', border:'1px solid rgba(16,185,129,0.3)' }}>
                  🛫 {source}
                </span>
                <div className="flex-1 h-px" style={{ background:'rgba(255,255,255,0.1)' }} />
                <span className="text-white/30 text-xs">→</span>
                <div className="flex-1 h-px" style={{ background:'rgba(255,255,255,0.1)' }} />
                <span className="px-3 py-1 rounded-full text-xs font-medium text-white"
                  style={{ background:'rgba(14,165,233,0.15)', border:'1px solid rgba(14,165,233,0.3)' }}>
                  📍 {destination}
                </span>
                {days && <span className="text-white/40 text-xs ml-2">{days}D · {travelers || 1}P</span>}
              </div>

              {/* Map */}
              <div className="flex-1 relative">
                {!mapReady && (
                  <div className="absolute inset-0 flex items-center justify-center z-10"
                    style={{ background:'rgba(2,8,23,0.9)' }}>
                    <div className="flex flex-col items-center gap-3">
                      <Navigation size={28} className="text-emerald-400 animate-pulse" />
                      <p className="text-white/50 text-sm">Plotting route…</p>
                    </div>
                  </div>
                )}
                <div id={mapId} className="w-full h-full" />
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
