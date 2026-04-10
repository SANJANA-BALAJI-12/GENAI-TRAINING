import { motion } from 'framer-motion';
import { CloudRain, Sun, Cloud, Droplets } from 'lucide-react';
import { useState, useEffect } from 'react';

export default function WeatherForecast() {
  const [forecastData, setForecastData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchWeather = async () => {
      try {
        const response = await fetch('/api/weather/forecast');
        if (response.ok) {
          const data = await response.json();
          setForecastData(data);
        }
      } catch (err) {
         console.error('Error fetching weather', err);
      } finally {
         setLoading(false);
      }
    };
    fetchWeather();
  }, []);

  const getIcon = (condition: string) => {
    switch(condition) {
      case 'Sun': return <Sun className="w-8 h-8 text-sun-300 drop-shadow-md" />;
      case 'Cloud': return <Cloud className="w-8 h-8 text-slate-300 drop-shadow-md" />;
      case 'CloudRain': return <CloudRain className="w-8 h-8 text-blue-300 drop-shadow-md" />;
      default: return <Sun className="w-8 h-8 text-sun-300 drop-shadow-md" />;
    }
  };

  const containerVariants = {
    hidden: { opacity: 0 },
    show: {
      opacity: 1,
      transition: { staggerChildren: 0.1 }
    }
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    show: { opacity: 1, y: 0 }
  };

  if (loading) {
    return (
      <div className="w-full h-96 flex justify-center items-center">
        <div className="w-12 h-12 border-4 border-nature-400 border-t-transparent rounded-full animate-spin"></div>
      </div>
    );
  }

  // Fallback in case of failure
  const data = forecastData || {
    irrigation_need: "High", moisture: 34, wind: "SSW 14 km/h", humidity: 62,
    forecast: [
        { day: 'Mon', temp: '24°C', condition: 'Sun' },
        { day: 'Tue', temp: '22°C', condition: 'Cloud' },
        { day: 'Wed', temp: '19°C', condition: 'CloudRain' },
        { day: 'Thu', temp: '20°C', condition: 'CloudRain' },
        { day: 'Fri', temp: '25°C', condition: 'Sun' },
        { day: 'Sat', temp: '26°C', condition: 'Sun' },
        { day: 'Sun', temp: '23°C', condition: 'Cloud' }
    ]
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <h1 className="text-4xl font-black text-white drop-shadow-lg tracking-wide">Hyperlocal Weather</h1>
          <p className="text-white/80 font-medium mt-2 tracking-wide">Farm Sector: Alpha (Lat: 34.05, Lon: -118.24)</p>
        </div>
        <motion.div whileHover={{ scale: 1.05 }} className="bg-nature-500/80 backdrop-blur-md text-white px-5 py-2.5 rounded-full shadow-lg border border-nature-400 text-sm font-bold flex items-center gap-3 cursor-pointer">
           <span className="w-2.5 h-2.5 bg-white rounded-full animate-pulse shadow-[0_0_8px_rgba(255,255,255,0.8)]"></span>
           Live Satellite Link
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        <motion.div initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} className="lg:col-span-3 glass-panel p-8 shadow-2xl border border-white/10">
           <h2 className="text-2xl font-bold text-white mb-8 drop-shadow-sm font-display">7-Day Prediction</h2>
           <motion.div variants={containerVariants} initial="hidden" animate="show" className="flex justify-between py-2 overflow-x-auto gap-4 scrollbar-hide">
             {data.forecast.map((day: any, idx: number) => (
                <motion.div variants={itemVariants} whileHover={{ y: -5, scale: 1.05 }} key={idx} className="flex flex-col items-center gap-5 min-w-[80px] p-4 rounded-2xl hover:bg-white/10 transition-colors border border-transparent hover:border-white/10 cursor-pointer">
                  <span className={`${idx === 0 ? 'text-nature-400' : 'text-white/70'} font-bold tracking-wider`}>{day.day}</span>
                  <div className={`p-4 rounded-full shadow-inner border border-white/20 backdrop-blur-md ${idx === 0 ? 'bg-nature-500/20' : 'bg-white/10'}`}>
                    {getIcon(day.condition)}
                  </div>
                  <span className="text-2xl font-black text-white">{day.temp}</span>
                </motion.div>
             ))}
           </motion.div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }} 
          animate={{ opacity: 1, x: 0 }} 
          transition={{ delay: 0.2 }} 
          className={`glass-panel p-8 bg-gradient-to-br ${data.irrigation_need === 'High' ? 'from-blue-600/60 to-blue-900/60' : 'from-green-600/60 to-green-900/60'} text-white flex flex-col justify-between shadow-2xl border-white/10`}
        >
            <div>
              <h3 className="font-bold text-blue-100 mb-5 flex items-center gap-3 text-lg tracking-wide font-display">
                <Droplets className="text-blue-300" /> Irrigation Need
              </h3>
              <p className="text-5xl font-black mb-3 drop-shadow-md">{data.irrigation_need}</p>
              <p className="text-sm font-medium text-blue-200 leading-relaxed">Soil moisture at {data.moisture}%. {data.irrigation_need === 'High' ? 'Increased watering advised.' : 'Optimal levels maintained.'}</p>
            </div>
            
            <div className="mt-8 bg-black/30 p-5 rounded-2xl backdrop-blur-md border border-white/10 shadow-inner">
               <div className="flex justify-between items-center text-sm mb-3">
                 <span className="text-blue-200/80">Wind</span>
                 <span className="font-bold tracking-wide">{data.wind}</span>
               </div>
               <div className="flex justify-between items-center text-sm">
                 <span className="text-blue-200/80">Humidity</span>
                 <span className="font-bold tracking-wide">{data.humidity}%</span>
               </div>
            </div>
        </motion.div>
      </div>
    </div>
  );
}
