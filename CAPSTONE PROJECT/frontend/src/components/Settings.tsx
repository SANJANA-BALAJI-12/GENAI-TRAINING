import { motion } from 'framer-motion';
import { Settings as SettingsIcon, Bell, Shield, Key, Database, ChevronRight } from 'lucide-react';
import { useState } from 'react';

export default function Settings() {
  const [notifications, setNotifications] = useState(true);
  const [dataSharing, setDataSharing] = useState(false);

  return (
    <div className="space-y-8 max-w-4xl mx-auto">
      <div className="mb-10 text-center md:text-left">
        <h1 className="text-4xl font-black text-white drop-shadow-lg flex justify-center md:justify-start items-center gap-4 font-display tracking-wide">
          <SettingsIcon className="w-10 h-10 text-white" />
          System Preferences
        </h1>
        <p className="text-white/80 mt-3 font-medium tracking-wide">Manage your AgriBlast platform configuration and API integrations.</p>
      </div>

      <div className="space-y-6">
        
        {/* API Keys Section */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-panel p-8 shadow-2xl border-l-[6px] border-l-nature-500 bg-slate-900/60 transition-all hover:bg-slate-900/70 cursor-pointer">
          <div className="flex items-center justify-between mb-8">
             <div className="flex items-center gap-4">
               <div className="p-3 bg-white/10 rounded-xl shadow-inner border border-white/20"><Key className="w-6 h-6 text-white" /></div>
               <h2 className="text-2xl font-bold text-white font-display tracking-wide">API Configurations</h2>
             </div>
             <ChevronRight className="text-white/30" />
          </div>
          
          <div className="space-y-6">
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-white/70 uppercase tracking-widest">Groq LLM Key</label>
              <input type="password" value="gsk_UIc0IQe2I0AOqPzMSCDhWGdyb3FYJs..." readOnly className="p-4 bg-black/40 border border-white/10 rounded-xl text-white/50 font-mono text-sm focus:outline-none shadow-inner" />
            </div>
            <div className="flex flex-col gap-2">
              <label className="text-xs font-bold text-white/70 uppercase tracking-widest">OpenAI Key</label>
              <input type="password" value="sk-proj-eZ0tvzF5oNjFNMdtPDLO98fQKzKE..." readOnly className="p-4 bg-black/40 border border-white/10 rounded-xl text-white/50 font-mono text-sm focus:outline-none shadow-inner" />
            </div>
            <p className="text-xs font-medium text-white/40 mt-2 bg-black/20 p-3 rounded-lg border border-white/5">Keys are securely stored in the backend environment. Do not share these publicly.</p>
          </div>
        </motion.div>

        {/* Sync Settings */}
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-panel p-8 shadow-xl border-l-[6px] border-l-blue-500 bg-slate-900/60 flex flex-col md:flex-row justify-between items-center gap-6">
          <div className="flex items-start gap-4">
            <div className="p-3 bg-white/10 rounded-xl shadow-inner border border-white/20"><Database className="w-6 h-6 text-white" /></div>
            <div>
              <h2 className="text-xl font-bold text-white tracking-wide font-display mb-1">Local ChromaDB Sync</h2>
              <p className="text-sm font-medium text-white/70">Last synced: Today, 08:30 AM <span className="mx-2 text-white/20">|</span> 14 documents indexed.</p>
            </div>
          </div>
          <motion.button whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }} className="px-6 py-3 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-full shadow-[0_0_15px_rgba(59,130,246,0.5)] transition-all">Force Sync</motion.button>
        </motion.div>

        {/* Toggles */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }} className="glass-panel p-8 shadow-xl bg-slate-900/60 flex justify-between items-center border border-white/10 hover:border-white/20 transition-all cursor-pointer" onClick={() => setNotifications(!notifications)}>
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl shadow-inner border border-white/20 transition-colors ${notifications ? 'bg-nature-500/20' : 'bg-white/10'}`}><Bell className={`w-6 h-6 ${notifications ? 'text-nature-400' : 'text-white/70'}`} /></div>
              <div>
                <h3 className="font-bold text-white tracking-wide font-display">Push Alerts</h3>
                <p className="text-xs text-white/60 font-medium mt-1 uppercase tracking-wider">Weather & Disease</p>
              </div>
            </div>
            <div className={`w-14 h-8 rounded-full p-1 transition-colors shadow-inner flex items-center ${notifications ? 'bg-nature-500' : 'bg-white/20'}`}>
              <motion.div layout className={`w-6 h-6 bg-white rounded-full shadow-md ${notifications ? 'ml-auto' : ''}`} />
            </div>
          </motion.div>

          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }} className="glass-panel p-8 shadow-xl bg-slate-900/60 flex justify-between items-center border border-white/10 hover:border-white/20 transition-all cursor-pointer" onClick={() => setDataSharing(!dataSharing)}>
            <div className="flex items-center gap-4">
              <div className={`p-3 rounded-xl shadow-inner border border-white/20 transition-colors ${dataSharing ? 'bg-blue-500/20' : 'bg-white/10'}`}><Shield className={`w-6 h-6 ${dataSharing ? 'text-blue-400' : 'text-white/70'}`} /></div>
              <div>
                <h3 className="font-bold text-white tracking-wide font-display">Data Sharing</h3>
                <p className="text-xs text-white/60 font-medium mt-1 uppercase tracking-wider">Anonymized Yields</p>
              </div>
            </div>
            <div className={`w-14 h-8 rounded-full p-1 transition-colors shadow-inner flex items-center ${dataSharing ? 'bg-blue-500' : 'bg-white/20'}`}>
              <motion.div layout className={`w-6 h-6 bg-white rounded-full shadow-md ${dataSharing ? 'ml-auto' : ''}`} />
            </div>
          </motion.div>
        </div>

      </div>
    </div>
  );
}
