import { useEffect, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, MapPin, Navigation } from 'lucide-react';

interface MarkerData {
  lat: number;
  lng: number;
  title: string;
  description?: string;
  category?: string;
}

interface MapModalProps {
  isOpen: boolean;
  onClose: () => void;
  title: string;
  markers: MarkerData[];
  center?: { lat: number; lng: number };
  zoom?: number;
}

// Lazy-load Leaflet only when map is opened

export default function MapModal({
  isOpen, onClose, title, markers, center, zoom = 10,
}: MapModalProps) {
  const [mapReady, setMapReady] = useState(false);
  const mapId = 'tripwise-map';

  // Default center: first marker or India center
  const mapCenter = center || (markers[0]
    ? { lat: markers[0].lat, lng: markers[0].lng }
    : { lat: 20.5937, lng: 78.9629 }
  );

  useEffect(() => {
    if (!isOpen) return;

    // Dynamically load Leaflet CSS
    if (!document.getElementById('leaflet-css')) {
      const link = document.createElement('link');
      link.id = 'leaflet-css';
      link.rel = 'stylesheet';
      link.href = 'https://unpkg.com/leaflet@1.9.4/dist/leaflet.css';
      document.head.appendChild(link);
    }

    // Small delay to let the modal render before initialising map
    const timer = setTimeout(() => {
      initMap();
      setMapReady(true);
    }, 200);

    return () => {
      clearTimeout(timer);
      // Destroy map instance on close to avoid re-init errors
      const container = document.getElementById(mapId) as any;
      if (container && container._leaflet_id) {
        container._leaflet_id = null;
      }
    };
  }, [isOpen]);

  const initMap = () => {
    import('leaflet').then((L) => {
      const container = document.getElementById(mapId);
      if (!container) return;

      // Clear previous instance
      if ((container as any)._leaflet_id) {
        (container as any)._leaflet_id = null;
      }

      const map = L.map(mapId, {
        center: [mapCenter.lat, mapCenter.lng],
        zoom,
        zoomControl: true,
      });

      // OpenStreetMap tiles — completely free, no API key
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '© <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
        maxZoom: 19,
      }).addTo(map);

      // Custom marker icon
      const icon = L.divIcon({
        html: `<div style="
          background: linear-gradient(135deg,#10b981,#0ea5e9);
          width:32px; height:32px; border-radius:50% 50% 50% 0;
          transform:rotate(-45deg); border:3px solid white;
          box-shadow:0 2px 8px rgba(0,0,0,0.4);
        "></div>`,
        iconSize: [32, 32],
        iconAnchor: [16, 32],
        popupAnchor: [0, -34],
        className: '',
      });

      // Add markers
      markers.forEach((m) => {
        if (!m.lat || !m.lng) return;
        L.marker([m.lat, m.lng], { icon })
          .addTo(map)
          .bindPopup(`
            <div style="font-family:Inter,sans-serif; min-width:160px;">
              <div style="font-weight:700; font-size:14px; margin-bottom:4px;">${m.title}</div>
              ${m.category ? `<div style="font-size:11px; color:#10b981; margin-bottom:4px; text-transform:uppercase; letter-spacing:.05em;">${m.category}</div>` : ''}
              ${m.description ? `<div style="font-size:12px; color:#555;">${m.description}</div>` : ''}
            </div>
          `, { maxWidth: 220 });
      });

      // Fit bounds if multiple markers
      if (markers.length > 1) {
        const valid = markers.filter(m => m.lat && m.lng);
        if (valid.length > 1) {
          const bounds = L.latLngBounds(valid.map(m => [m.lat, m.lng]));
          map.fitBounds(bounds, { padding: [40, 40] });
        }
      }
    });
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div key="map-backdrop"
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={onClose}
            className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm" />

          {/* Modal */}
          <motion.div key="map-modal"
            initial={{ opacity: 0, scale: 0.96, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.96, y: 20 }}
            transition={{ duration: 0.25 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 pointer-events-none">

            <div className="w-full max-w-4xl h-[600px] pointer-events-auto rounded-2xl overflow-hidden flex flex-col"
              style={{ background: 'rgba(2,8,23,0.98)', border: '1px solid rgba(255,255,255,0.12)', boxShadow: '0 40px 80px rgba(0,0,0,0.7)' }}>

              {/* Header */}
              <div className="flex items-center justify-between px-5 py-4 flex-shrink-0"
                style={{ borderBottom: '1px solid rgba(255,255,255,0.08)' }}>
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg flex items-center justify-center"
                    style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                    <MapPin size={16} className="text-white" />
                  </div>
                  <div>
                    <h3 className="text-white font-semibold text-sm">{title}</h3>
                    <p className="text-white/40 text-xs">{markers.length} location{markers.length !== 1 ? 's' : ''} · OpenStreetMap</p>
                  </div>
                </div>
                <button onClick={onClose}
                  className="w-8 h-8 rounded-full flex items-center justify-center text-white/60 hover:text-white transition-colors"
                  style={{ background: 'rgba(255,255,255,0.08)' }}>
                  <X size={16} />
                </button>
              </div>

              {/* Legend */}
              {markers.length > 0 && (
                <div className="flex gap-3 px-5 py-2 overflow-x-auto flex-shrink-0"
                  style={{ borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                  {markers.slice(0, 6).map((m, i) => (
                    <div key={i} className="flex items-center gap-1.5 flex-shrink-0">
                      <div className="w-2 h-2 rounded-full" style={{ background: 'linear-gradient(135deg,#10b981,#0ea5e9)' }} />
                      <span className="text-white/60 text-xs whitespace-nowrap">{m.title}</span>
                    </div>
                  ))}
                  {markers.length > 6 && <span className="text-white/30 text-xs">+{markers.length - 6} more</span>}
                </div>
              )}

              {/* Map container */}
              <div className="flex-1 relative">
                {!mapReady && (
                  <div className="absolute inset-0 flex items-center justify-center z-10"
                    style={{ background: 'rgba(2,8,23,0.9)' }}>
                    <div className="flex flex-col items-center gap-3">
                      <Navigation size={28} className="text-emerald-400 animate-pulse" />
                      <p className="text-white/50 text-sm">Loading map…</p>
                    </div>
                  </div>
                )}
                <div id={mapId} className="w-full h-full" style={{ minHeight: '400px' }} />
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
