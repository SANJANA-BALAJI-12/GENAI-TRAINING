import React, { useState, useEffect, useRef } from 'react';
import { Leaf, Mic, CloudRain, Info, Send, Search, Settings as SettingsIcon, MessageSquare } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

// Import Views
import Dashboard from './components/Dashboard';
import CropAnalysis from './components/CropAnalysis';
import WeatherForecast from './components/WeatherForecast';
import Community from './components/Community';
import Settings from './components/Settings';

export default function App() {
  const [currentView, setCurrentView] = useState('Dashboard');
  const [chatOpen, setChatOpen] = useState(false);
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const chatEndRef = useRef<HTMLDivElement>(null);
  
  const [chatHistory, setChatHistory] = useState([
    { role: 'assistant', content: 'Hello! I am your AI Smart Farming Advisor. My CrewAI agents are ready. Try asking about weather logic, crop yields, or disease control!' }
  ]);

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory, isTyping]);

  const handleSendMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!message.trim()) return;
    
    setChatHistory(prev => [...prev, { role: 'user', content: message }]);
    const currentMessage = message;
    setMessage('');
    setIsTyping(true);
    
    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: currentMessage,
          location: 'local', // Could be made dynamic later
          language: 'en'
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from AI assistant');
      }

      const data = await response.json();
      setChatHistory(prev => [...prev, { role: 'assistant', content: data.reply }]);
    } catch (error) {
      console.error('Error sending message:', error);
      setChatHistory(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error while processing your request. Please check that the backend server is running and try again.' 
      }]);
    } finally {
      setIsTyping(false);
    }
  };

  const renderView = () => {
    switch(currentView) {
      case 'Dashboard': return <Dashboard />;
      case 'Crop Analysis': return <CropAnalysis />;
      case 'Weather Forecast': return <WeatherForecast />;
      case 'Community': return <Community />;
      case 'Settings': return <Settings />;
      default: return <Dashboard />;
    }
  };

  const getBackground = () => {
    switch(currentView) {
      case 'Weather Forecast': return '/bg_weather.png';
      case 'Crop Analysis': return '/bg_crop.png';
      case 'Settings': return '/bg_settings.png';
      case 'Community': 
      case 'Dashboard': 
      default: return '/bg_dashboard.png';
    }
  };

  const navItems = [
    { name: 'Dashboard', icon: <Info size={18} /> },
    { name: 'Crop Analysis', icon: <Search size={18} /> },
    { name: 'Weather Forecast', icon: <CloudRain size={18} /> },
    { name: 'Community', icon: <MessageSquare size={18} /> },
    { name: 'Settings', icon: <SettingsIcon size={18} /> }
  ];

  return (
    <div className="min-h-screen flex text-slate-800 bg-black fixed inset-0 font-sans overflow-hidden">
      
      {/* Dynamic Background Image layer with subtle fade between transitions */}
      <AnimatePresence mode="wait">
        <motion.div
           key={currentView}
           initial={{ opacity: 0.5 }}
           animate={{ opacity: 1 }}
           exit={{ opacity: 0.5 }}
           transition={{ duration: 0.8 }}
           className="absolute inset-0 bg-cover bg-center bg-no-repeat"
           style={{ backgroundImage: `linear-gradient(rgba(0,0,0,0.4), rgba(0,0,0,0.4)), url('${getBackground()}')` }}
        />
      </AnimatePresence>
      
      {/* Sidebar Navigation */}
      <nav className="w-20 lg:w-72 glass-panel border-l-0 border-t-0 border-b-0 rounded-none m-0 flex flex-col justify-between hidden sm:flex transition-all duration-300 z-10 bg-white/10 border-r-white/10 shadow-[5px_0_30px_rgba(0,0,0,0.1)]">
        <div>
          <div className="h-24 flex items-center justify-center lg:justify-start lg:px-8 border-b border-white/10">
            <motion.div whileHover={{ rotate: 10 }} className="bg-nature-500 p-2 rounded-xl shadow-[0_0_15px_rgba(34,197,94,0.5)]">
              <Leaf className="text-white w-8 h-8" />
            </motion.div>
            <span className="ml-4 font-bold text-2xl hidden lg:block tracking-wide drop-shadow-md text-white font-display">AgriBlast <span className="text-nature-400">AI</span></span>
          </div>
          <div className="mt-8 flex flex-col gap-3 px-4">
            {navItems.map((item) => (
              <motion.div 
                whileHover={{ x: 5 }}
                whileTap={{ scale: 0.98 }}
                key={item.name} 
                onClick={() => setCurrentView(item.name)}
                className={`flex items-center gap-4 px-4 py-4 rounded-xl cursor-pointer transition-all duration-200 ease-in-out ${
                  currentView === item.name 
                    ? 'bg-nature-600 shadow-md border-transparent text-white font-bold' 
                    : 'hover:bg-white/20 text-slate-900 border border-transparent font-medium hover:shadow-sm backdrop-blur-sm'
                }`}
              >
                <div className={`flex items-center justify-center ${currentView === item.name ? 'text-white' : 'text-slate-800'}`}>
                   {item.icon}
                </div>
                <span className="hidden lg:block text-lg">{item.name}</span>
              </motion.div>
            ))}
          </div>
        </div>
        
        <div className="p-6 border-t border-white/10 hidden lg:block">
          <div className="bg-white/20 backdrop-blur-md rounded-2xl p-5 border border-white/20 relative overflow-hidden group shadow-xl">
            <div className="absolute top-0 right-0 w-24 h-24 bg-nature-500 rounded-bl-full opacity-20 group-hover:scale-125 transition-transform duration-500"></div>
            <p className="text-slate-900 text-sm font-bold mb-2">System Status</p>
            <div className="flex items-center gap-3">
              <div className="w-3 h-3 bg-nature-500 rounded-full shadow-[0_0_10px_rgba(34,197,94,0.8)] animate-pulse"></div>
              <span className="font-bold text-slate-800 tracking-wide">Agents Online</span>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content Area */}
      <main className="flex-1 overflow-y-auto relative z-10 w-full h-full pb-24">
        
        {/* Top Header */}
        <header className="h-24 px-10 flex items-center justify-between sticky top-0 z-20 glass-panel rounded-none border-t-0 border-l-0 border-r-0 border-b-white/10 shadow-sm">
          <div>
            <h2 className="text-sm font-bold text-nature-300 uppercase letter tracking-widest mb-1">{currentView}</h2>
            <p className="text-white text-sm font-medium">AgriBlast Precision Farming Suite</p>
          </div>
          <motion.div whileHover={{ scale: 1.05 }} className="flex bg-white/10 backdrop-blur-md border border-white/20 shadow-lg rounded-full px-5 py-2.5 items-center gap-3 cursor-pointer">
             <div className="w-2.5 h-2.5 bg-nature-400 rounded-full shadow-[0_0_8px_rgba(74,222,128,0.8)]"></div>
             <span className="text-sm font-bold text-white">Sensors Connected</span>
          </motion.div>
        </header>

        {/* View Injection */}
        <div className="relative p-4 md:p-8">
          <AnimatePresence mode="wait">
            <motion.div
              key={currentView}
              initial={{ opacity: 0, y: 15 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -15 }}
              transition={{ duration: 0.3 }}
            >
              {renderView()}
            </motion.div>
          </AnimatePresence>
        </div>
      </main>

      {/* Floating Chat Interface */}
      <AnimatePresence>
        {chatOpen && (
          <motion.div 
            initial={{ opacity: 0, y: 50, scale: 0.9, rotateX: 10 }}
            animate={{ opacity: 1, y: 0, scale: 1, rotateX: 0 }}
            exit={{ opacity: 0, y: 30, scale: 0.95, rotateX: -5 }}
            transition={{ type: "spring", damping: 25, stiffness: 300 }}
            className="fixed bottom-[100px] right-8 w-[400px] h-[650px] glass-panel z-50 flex flex-col overflow-hidden bg-slate-900/40 border-white/20 shadow-2xl backdrop-blur-xl"
          >
            {/* Header */}
            <div className="bg-gradient-to-r from-nature-600 to-nature-500 p-5 text-white flex justify-between items-center shadow-md z-10 border-b border-nature-400/50">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-full bg-white/20 flex items-center justify-center border border-white/30 backdrop-blur-sm shadow-inner relative">
                  <div className="absolute top-0 right-0 w-3.5 h-3.5 bg-nature-300 shadow-[0_0_10px_rgba(134,239,172,1)] border-2 border-nature-600 rounded-full"></div>
                  <Leaf className="w-6 h-6 text-white drop-shadow-md" />
                </div>
                <div>
                  <h3 className="font-bold text-lg leading-tight tracking-wide font-display">Smart Advisor</h3>
                  <p className="text-xs text-nature-100 opacity-90 tracking-wider font-medium">CrewAI Multi-Agent System</p>
                </div>
              </div>
              <button 
                onClick={() => setChatOpen(false)}
                className="w-8 h-8 flex items-center justify-center hover:bg-white/20 rounded-full transition-colors font-bold text-lg"
               >
                &times;
              </button>
            </div>

            {/* Chat History */}
            <div className="flex-1 p-5 overflow-y-auto flex flex-col gap-5">
              {chatHistory.map((msg, idx) => (
                <motion.div 
                  initial={{ opacity: 0, y: 10, scale: 0.95 }}
                  animate={{ opacity: 1, y: 0, scale: 1 }}
                  key={idx} 
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  {msg.role === 'assistant' && (
                     <div className="w-8 h-8 rounded-full bg-nature-500 border border-white/20 flex items-center justify-center mr-2 shadow-sm shrink-0 mt-1">
                       <Leaf className="w-4 h-4 text-white" />
                     </div>
                  )}
                  <div className={`max-w-[80%] p-4 rounded-2xl shadow-md text-sm leading-relaxed ${
                    msg.role === 'user' 
                      ? 'bg-nature-600 text-white rounded-tr-none border border-nature-500' 
                      : 'bg-white/90 backdrop-blur-sm text-slate-800 rounded-tl-none border border-white'
                  }`}>
                    {msg.content}
                  </div>
                </motion.div>
              ))}
              
              {isTyping && (
                <motion.div 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  className="flex justify-start items-end"
                >
                  <div className="w-8 h-8 rounded-full bg-nature-500 border border-white/20 flex items-center justify-center mr-2 shadow-sm shrink-0">
                    <Leaf className="w-4 h-4 text-white" />
                  </div>
                  <div className="bg-white/90 backdrop-blur-sm p-4 rounded-2xl rounded-tl-none flex gap-1 items-center border border-white">
                    <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.3s]"></span>
                    <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce [animation-delay:-0.15s]"></span>
                    <span className="w-2 h-2 bg-slate-400 rounded-full animate-bounce"></span>
                  </div>
                </motion.div>
              )}
              <div ref={chatEndRef} />
            </div>

            {/* Input Area */}
            <div className="p-4 bg-white/10 backdrop-blur-xl border-t border-white/20">
              <form onSubmit={handleSendMessage} className="flex gap-2 relative items-center">
                <button type="button" className="p-2 text-white/70 hover:text-white transition-colors rounded-full shrink-0">
                   <Mic size={22} />
                </button>
                <input 
                  type="text" 
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Ask about crops, disease, or yield..."
                  className="flex-1 bg-white/20 border border-white/30 text-white focus:bg-white/30 focus:border-nature-400 focus:ring-1 focus:ring-nature-400 rounded-full px-5 py-3 outline-none text-sm transition-all placeholder:text-white/60 shadow-inner"
                />
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  type="submit" 
                  disabled={!message.trim() || isTyping} 
                  className="bg-nature-500 hover:bg-nature-400 disabled:opacity-50 disabled:hover:bg-nature-500 text-white p-3 rounded-full shrink-0 shadow-[0_0_15px_rgba(34,197,94,0.4)] transition-all"
                >
                  <Send size={20} className="-ml-0.5 mt-0.5" />
                </motion.button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* FAB Button */}
      <motion.button 
        whileHover={{ scale: 1.05, y: -2 }}
        whileTap={{ scale: 0.95 }}
        onClick={() => setChatOpen(!chatOpen)}
        className="fixed bottom-8 right-8 w-20 h-20 bg-gradient-to-tr from-sun-400 to-nature-500 text-white rounded-full shadow-[0_10px_25px_rgba(0,0,0,0.3)] flex items-center justify-center z-40 relative group border-2 border-white/20"
      >
        <div className="absolute inset-0 rounded-full bg-white opacity-0 group-hover:opacity-20 transition-opacity"></div>
        {chatOpen ? <span className="font-bold text-3xl font-display">&times;</span> : <MessageSquare className="w-8 h-8 filter drop-shadow-md" />}
      </motion.button>
      
    </div>
  );
}
