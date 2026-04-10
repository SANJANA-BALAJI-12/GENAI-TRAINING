import { motion } from 'framer-motion';
import { MapPin, Eye, Zap, Droplets } from 'lucide-react';
import { useState } from 'react';

interface FarmSector {
  id: string;
  name: string;
  ndvi: number;
  status: 'healthy' | 'stressed' | 'critical';
  area: number;
  coordinates: [number, number];
}

export default function FieldMapping() {
  const [selectedSector, setSelectedSector] = useState<string | null>(null);
  const [viewMode, setViewMode] = useState<'ndvi' | 'topography'>('ndvi');

  // Mock farm sectors with NDVI data
  const sectors: FarmSector[] = [
    {
      id: 'alpha',
      name: 'Sector Alpha',
      ndvi: 0.78,
      status: 'healthy',
      area: 45.2,
      coordinates: [40.7128, -74.0060]
    },
    {
      id: 'beta',
      name: 'Sector Beta',
      ndvi: 0.45,
      status: 'stressed',
      area: 32.8,
      coordinates: [40.7128, -74.0060]
    },
    {
      id: 'gamma',
      name: 'Sector Gamma',
      ndvi: 0.23,
      status: 'critical',
      area: 28.5,
      coordinates: [40.7128, -74.0060]
    }
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-400';
      case 'stressed': return 'text-yellow-400';
      case 'critical': return 'text-red-400';
      default: return 'text-gray-400';
    }
  };

  const getNDVIColor = (ndvi: number) => {
    if (ndvi >= 0.7) return 'from-green-500 to-green-600';
    if (ndvi >= 0.5) return 'from-yellow-500 to-yellow-600';
    return 'from-red-500 to-red-600';
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold text-white drop-shadow-md tracking-wide">Field Mapping & NDVI Analysis</h2>
        <div className="flex gap-2">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setViewMode('ndvi')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'ndvi'
                ? 'bg-nature-500 text-white'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            <Eye className="w-4 h-4 inline mr-2" />
            NDVI View
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setViewMode('topography')}
            className={`px-4 py-2 rounded-lg font-medium transition-colors ${
              viewMode === 'topography'
                ? 'bg-nature-500 text-white'
                : 'bg-white/10 text-white/70 hover:bg-white/20'
            }`}
          >
            <MapPin className="w-4 h-4 inline mr-2" />
            Topography
          </motion.button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Map Visualization */}
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          className="lg:col-span-2 glass-panel p-6"
        >
          <div className="relative h-96 bg-slate-900/60 rounded-xl overflow-hidden border border-white/10">
            {/* Mock satellite map background */}
            <div className="absolute inset-0 bg-gradient-to-br from-slate-800 to-slate-900">
              {/* Grid lines */}
              <div className="absolute inset-0 opacity-20">
                {Array.from({ length: 10 }).map((_, i) => (
                  <div key={`h-${i}`} className="absolute w-full h-px bg-white/20" style={{ top: `${i * 10}%` }} />
                ))}
                {Array.from({ length: 10 }).map((_, i) => (
                  <div key={`v-${i}`} className="absolute h-full w-px bg-white/20" style={{ left: `${i * 10}%` }} />
                ))}
              </div>

              {/* Farm sectors */}
              {sectors.map((sector, index) => (
                <motion.div
                  key={sector.id}
                  initial={{ opacity: 0, scale: 0 }}
                  animate={{ opacity: 1, scale: 1 }}
                  transition={{ delay: index * 0.2 }}
                  whileHover={{ scale: 1.1 }}
                  onClick={() => setSelectedSector(sector.id)}
                  className={`absolute cursor-pointer border-2 border-white/50 rounded-lg flex items-center justify-center font-bold text-white shadow-lg ${
                    selectedSector === sector.id ? 'ring-4 ring-white/50' : ''
                  }`}
                  style={{
                    left: `${20 + index * 25}%`,
                    top: `${30 + (index % 2) * 20}%`,
                    width: '120px',
                    height: '80px',
                    background: `linear-gradient(135deg, ${getNDVIColor(sector.ndvi).split(' ')[0].replace('from-', '')}, ${getNDVIColor(sector.ndvi).split(' ')[1].replace('to-', '')})`
                  }}
                >
                  <div className="text-center">
                    <div className="text-sm font-bold">{sector.name}</div>
                    <div className="text-xs opacity-80">NDVI: {(sector.ndvi * 100).toFixed(0)}%</div>
                  </div>
                </motion.div>
              ))}

              {/* Legend */}
              <div className="absolute bottom-4 left-4 bg-black/60 backdrop-blur-md rounded-lg p-3 text-white text-xs">
                <div className="font-bold mb-2">NDVI Legend</div>
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-green-500 rounded"></div>
                    <span>Healthy (70%+)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-yellow-500 rounded"></div>
                    <span>Stressed (50-70%)</span>
                  </div>
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 bg-red-500 rounded"></div>
                    <span>Critical (&lt;50%)</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </motion.div>

        {/* Sector Details */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-panel p-6"
        >
          <h3 className="text-xl font-bold text-white mb-4">Sector Analysis</h3>

          {selectedSector ? (
            <div className="space-y-4">
              {(() => {
                const sector = sectors.find(s => s.id === selectedSector);
                if (!sector) return null;

                return (
                  <>
                    <div className="bg-white/10 rounded-lg p-4">
                      <h4 className="font-bold text-white text-lg mb-2">{sector.name}</h4>
                      <div className="space-y-2 text-sm">
                        <div className="flex justify-between">
                          <span className="text-white/70">Area:</span>
                          <span className="text-white font-medium">{sector.area} acres</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/70">NDVI Index:</span>
                          <span className={`font-medium ${getStatusColor(sector.status)}`}>
                            {(sector.ndvi * 100).toFixed(1)}%
                          </span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-white/70">Status:</span>
                          <span className={`font-medium capitalize ${getStatusColor(sector.status)}`}>
                            {sector.status}
                          </span>
                        </div>
                      </div>
                    </div>

                    <div className="bg-white/10 rounded-lg p-4">
                      <h5 className="font-semibold text-white mb-3">Recommendations</h5>
                      <ul className="space-y-2 text-sm text-white/80">
                        {sector.status === 'critical' && (
                          <>
                            <li className="flex items-start gap-2">
                              <Droplets className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                              <span>Immediate irrigation needed - soil moisture critical</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <Zap className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                              <span>Apply nitrogen fertilizer within 24 hours</span>
                            </li>
                          </>
                        )}
                        {sector.status === 'stressed' && (
                          <>
                            <li className="flex items-start gap-2">
                              <Droplets className="w-4 h-4 text-blue-400 mt-0.5 flex-shrink-0" />
                              <span>Schedule irrigation for next 48 hours</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <Eye className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                              <span>Monitor closely for disease development</span>
                            </li>
                          </>
                        )}
                        {sector.status === 'healthy' && (
                          <>
                            <li className="flex items-start gap-2">
                              <Eye className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
                              <span>Maintain current management practices</span>
                            </li>
                            <li className="flex items-start gap-2">
                              <Zap className="w-4 h-4 text-yellow-400 mt-0.5 flex-shrink-0" />
                              <span>Prepare for upcoming harvest season</span>
                            </li>
                          </>
                        )}
                      </ul>
                    </div>
                  </>
                );
              })()}
            </div>
          ) : (
            <div className="text-center text-white/60 py-8">
              <MapPin className="w-12 h-12 mx-auto mb-4 opacity-50" />
              <p>Select a sector on the map to view detailed analysis</p>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}