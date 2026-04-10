import { motion } from 'framer-motion';
import { ThermometerSun, Wind, Leaf, MapPin, CheckSquare } from 'lucide-react';
import { useState, useEffect } from 'react';
import FieldMapping from './FieldMapping';
import TaskInventory from './TaskInventory';

interface DashboardInsights {
  disease_alerts: string[];
  yield_predictions: string[];
  recommendations: string[];
}

export default function Dashboard() {
  const [insights, setInsights] = useState<DashboardInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeSection, setActiveSection] = useState<'overview' | 'mapping' | 'operations'>('overview');

  useEffect(() => {
    fetchInsights();
  }, []);

  const fetchInsights = async () => {
    try {
      const response = await fetch('/api/insights');
      if (response.ok) {
        const data = await response.json();
        setInsights(data);
      }
    } catch (error) {
      console.error('Error fetching insights:', error);
    } finally {
      setLoading(false);
    }
  };
  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Navigation Tabs */}
      <div className="flex justify-center">
        <div className="flex bg-white/10 rounded-lg p-1 backdrop-blur-md">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveSection('overview')}
            className={`px-6 py-3 rounded-md font-medium transition-colors flex items-center gap-2 ${
              activeSection === 'overview'
                ? 'bg-nature-500 text-white'
                : 'text-white/70 hover:text-white'
            }`}
          >
            <Leaf className="w-4 h-4" />
            Overview
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveSection('mapping')}
            className={`px-6 py-3 rounded-md font-medium transition-colors flex items-center gap-2 ${
              activeSection === 'mapping'
                ? 'bg-nature-500 text-white'
                : 'text-white/70 hover:text-white'
            }`}
          >
            <MapPin className="w-4 h-4" />
            Field Mapping
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={() => setActiveSection('operations')}
            className={`px-6 py-3 rounded-md font-medium transition-colors flex items-center gap-2 ${
              activeSection === 'operations'
                ? 'bg-nature-500 text-white'
                : 'text-white/70 hover:text-white'
            }`}
          >
            <CheckSquare className="w-4 h-4" />
            Operations
          </motion.button>
        </div>
      </div>

      {/* Content based on active section */}
      {activeSection === 'overview' && (
        <>
          {/* Hero Banner Grid Area */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            
            {/* Weather Widget */}
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="lg:col-span-2 relative overflow-hidden glass-panel bg-gradient-to-br from-nature-800/80 to-slate-900/80 text-white p-8 group"
            >
              <div className="absolute -right-10 -top-10 w-64 h-64 bg-white/5 rounded-full blur-3xl group-hover:bg-white/10 transition-colors duration-500"></div>
              <div className="flex justify-between items-start relative z-10">
                <div>
                  <div className="flex items-center gap-2 mb-1">
                    <ThermometerSun className="w-5 h-5 text-sun-300 drop-shadow-md" />
                    <span className="font-medium text-nature-100 tracking-wide font-sans">Local Weather</span>
                  </div>
                  <h2 className="text-6xl font-black mb-2 flex items-center font-display drop-shadow-lg">24°C</h2>
                  <p className="text-nature-50 font-medium font-sans">Partly Cloudy • Humidity 62%</p>
                </div>
                <div className="text-right">
                  <motion.div animate={{ rotate: 360 }} transition={{ duration: 40, repeat: Infinity, ease: "linear" }}>
                    <Wind className="w-14 h-14 text-white/50 drop-shadow-lg" />
                  </motion.div>
                </div>
              </div>
              <div className="mt-8 flex gap-4 relative z-10">
                <motion.div whileHover={{ y: -2 }} className="bg-white/10 backdrop-blur-md rounded-xl py-3 px-5 border border-white/20 flex-1 shadow-sm">
                  <p className="text-xs text-nature-100 font-semibold mb-1 uppercase tracking-wider">Precipitation</p>
                  <p className="text-xl font-bold font-display">12%</p>
                </motion.div>
                <motion.div whileHover={{ y: -2 }} className="bg-white/10 backdrop-blur-md rounded-xl py-3 px-5 border border-white/20 flex-1 shadow-sm">
                  <p className="text-xs text-nature-100 font-semibold mb-1 uppercase tracking-wider">Wind Speed</p>
                  <p className="text-xl font-bold font-display">14 km/h</p>
                </motion.div>
              </div>
            </motion.div>

            {/* Quick Action / Crop Status Widget */}
            <motion.div 
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.1 }}
              className="glass-panel p-6 flex flex-col justify-between hover:bg-white/20 transition-all duration-300"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 bg-white/20 rounded-full flex items-center justify-center border border-white/30 shadow-inner">
                  <Leaf className="w-6 h-6 text-white drop-shadow-sm" />
                </div>
                <span className="bg-nature-500/80 backdrop-blur-md text-white text-xs font-bold px-3 py-1.5 rounded-full uppercase tracking-wider shadow-sm border border-nature-400">Optimal</span>
              </div>
              <div>
                <h3 className="text-white/80 font-medium text-sm mb-1 font-sans">Current Focus</h3>
                <p className="text-3xl font-bold text-white font-display leading-tight drop-shadow-sm">Wheat Harvesting</p>
                <div className="w-full bg-slate-900/40 backdrop-blur-sm h-2.5 mt-5 rounded-full overflow-hidden shadow-inner border border-white/10">
                   <motion.div 
                      initial={{ width: 0 }}
                      animate={{ width: "65%" }}
                      transition={{ duration: 1, delay: 0.5 }}
                      className="bg-gradient-to-r from-sun-400 to-nature-400 h-full rounded-full shadow-[0_0_10px_rgba(250,204,21,0.6)]"
                    ></motion.div>
                </div>
                <p className="text-xs text-right mt-2 text-white/70 font-semibold tracking-wide">65% Readiness</p>
              </div>
            </motion.div>
          </div>

          {/* Activity / Notifications Area */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}>
            <h2 className="text-2xl font-bold text-white mb-5 drop-shadow-md tracking-wide">AI Agent Insights</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
              {loading ? (
                // Loading state
                Array.from({ length: 4 }).map((_, idx) => (
                  <motion.div 
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + (idx * 0.1) }}
                    key={idx} 
                    className="p-6 rounded-2xl bg-slate-900/60 backdrop-blur-xl shadow-lg border-y border-r border-white/10 border-l-4 border-l-slate-500 animate-pulse"
                  >
                    <div className="h-5 bg-white/20 rounded mb-2"></div>
                    <div className="h-4 bg-white/10 rounded"></div>
                  </motion.div>
                ))
              ) : insights ? (
                // Real insights from API
                [
                  ...insights.disease_alerts.slice(0, 2).map((alert) => ({
                    title: 'Disease Risk Alert',
                    detail: alert,
                    color: 'border-l-orange-400',
                    bg: 'bg-slate-900/60'
                  })),
                  ...insights.yield_predictions.slice(0, 2).map((prediction) => ({
                    title: 'Yield Prediction',
                    detail: prediction,
                    color: 'border-l-nature-400',
                    bg: 'bg-slate-900/60'
                  }))
                ].map((insight, idx) => (
                  <motion.div 
                    whileHover={{ y: -4, scale: 1.01 }}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + (idx * 0.1) }}
                    key={idx} 
                    className={`p-6 rounded-2xl ${insight.bg} backdrop-blur-xl shadow-lg border-y border-r border-white/10 ${insight.color} border-l-4 cursor-pointer`}
                  >
                     <h4 className="font-bold text-white font-display text-lg mb-1">{insight.title}</h4>
                     <p className="text-white/70 text-sm font-medium leading-relaxed">{insight.detail}</p>
                  </motion.div>
                ))
              ) : (
                // Fallback static insights
                [
                  { title: 'Disease Risk Alert', detail: 'Conditions favor Rust in Sector 4. Preventative spray recommended today.', color: 'border-l-orange-400', bg: 'bg-slate-900/60' },
                  { title: 'Yield Prediction Updated', detail: 'Based on recent rain, estimated yield increased by +4.2%.', color: 'border-l-nature-400', bg: 'bg-slate-900/60' }
                ].map((insight, idx) => (
                  <motion.div 
                    whileHover={{ y: -4, scale: 1.01 }}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: 0.3 + (idx * 0.1) }}
                    key={idx} className={`p-6 rounded-2xl ${insight.bg} backdrop-blur-xl shadow-lg border-y border-r border-white/10 ${insight.color} border-l-4 cursor-pointer`}
                  >
                     <h4 className="font-bold text-white font-display text-lg mb-1">{insight.title}</h4>
                     <p className="text-white/70 text-sm font-medium leading-relaxed">{insight.detail}</p>
                  </motion.div>
                ))
              )}
            </div>
          </motion.div>
        </>
      )}

      {activeSection === 'mapping' && <FieldMapping />}
      {activeSection === 'operations' && <TaskInventory />}
    </div>
  );
}
