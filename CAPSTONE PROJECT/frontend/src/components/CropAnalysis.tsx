import { motion, AnimatePresence } from 'framer-motion';
import { Search, Upload, AlertTriangle, CheckCircle, Leaf } from 'lucide-react';
import { useState, useRef } from 'react';

interface AnalysisResult {
  disease_detected: string;
  confidence: number;
  recommendation: string;
}

export default function CropAnalysis() {
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      handleUpload(file);
    }
  };

  const handleUpload = async (file?: File) => {
    const fileToUpload = file || selectedFile;
    if (!fileToUpload) return;

    setAnalyzing(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', fileToUpload);

      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Failed to analyze image');
      }

      const data: AnalysisResult = await response.json();
      setResult(data);
    } catch (error) {
      console.error('Error uploading image:', error);
      // Show error state
      setResult({
        disease_detected: 'Analysis Failed',
        confidence: 0,
        recommendation: 'Unable to analyze the image. Please try again with a clearer photo of the crop or plant.'
      });
    } finally {
      setAnalyzing(false);
    }
  };

  const handleDropZoneClick = () => {
    fileInputRef.current?.click();
  };

  const resetAnalysis = () => {
    setResult(null);
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="mb-6">
        <h1 className="text-4xl font-black text-white drop-shadow-lg tracking-wide font-display">Crop Disease Analysis</h1>
        <p className="text-white/80 mt-2 font-medium">Upload an image of a leaf to detect potential blights or deficiencies.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          whileHover={{ scale: 1.01 }}
          className="glass-panel p-8 flex flex-col items-center justify-center border-dashed border-2 border-white/40 hover:bg-white/10 hover:border-nature-400 transition-all cursor-pointer min-h-[450px] shadow-xl group"
          onClick={handleDropZoneClick}
        >
          <input
            type="file"
            ref={fileInputRef}
            onChange={handleFileSelect}
            accept="image/*"
            className="hidden"
          />
          
          {analyzing ? (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="text-center space-y-6">
              <div className="w-20 h-20 border-4 border-white/20 border-t-nature-400 rounded-full animate-spin mx-auto shadow-lg"></div>
              <h3 className="text-2xl font-bold text-white font-display tracking-wide">AI Agents Analyzing...</h3>
              <p className="text-white/70 font-medium max-w-sm mx-auto">Processing image with OpenAI Vision API and cross-referencing with agricultural databases.</p>
            </motion.div>
          ) : result ? (
            <motion.div initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} className="text-center space-y-6">
               <div className="w-40 h-40 bg-white/10 backdrop-blur-md rounded-3xl mx-auto overflow-hidden shadow-inner border border-white/20 flex items-center justify-center relative">
                 {selectedFile && (
                   <img 
                     src={URL.createObjectURL(selectedFile)} 
                     alt="Crop preview" 
                     className="absolute inset-0 w-full h-full object-cover" 
                   />
                 )}
                 <div className="absolute inset-0 border-[4px] border-orange-500/50 rounded-3xl"></div>
                 <Leaf className="w-16 h-16 text-white drop-shadow-lg z-10" />
               </div>
               <p className="font-bold text-white/90 tracking-wider">{selectedFile?.name || 'analyzed_image.jpg'}</p>
               <motion.button 
                 whileHover={{ scale: 1.05 }}
                 whileTap={{ scale: 0.95 }}
                 onClick={(e) => { e.stopPropagation(); resetAnalysis(); }} 
                 className="px-6 py-3 bg-white hover:bg-slate-100 rounded-full text-sm font-black text-slate-900 transition-colors shadow-lg"
               >
                 Analyze Another Image
               </motion.button>
            </motion.div>
          ) : (
            <div className="text-center space-y-6 p-4">
              <motion.div 
                whileHover={{ y: -5 }} 
                className="w-24 h-24 bg-white/10 backdrop-blur-md rounded-full flex items-center justify-center mx-auto shadow-inner border border-white/20 group-hover:bg-nature-500/20 transition-colors"
                >
                <Upload className="w-10 h-10 text-white drop-shadow-md" />
              </motion.div>
              <div>
                <h3 className="text-2xl font-bold text-white tracking-wide font-display">Upload Crop Image</h3>
                <p className="text-white/70 mt-3 font-medium">Click to select or drag and drop an image of your crop, plant, or soil for AI analysis.</p>
              </div>
            </div>
          )}
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-panel p-8 flex flex-col h-full shadow-xl bg-slate-900/60"
        >
          <h2 className="text-2xl font-bold text-white border-b border-white/20 pb-5 mb-6 font-display tracking-wide drop-shadow-sm">Diagnostics Report</h2>
          
          <AnimatePresence mode="wait">
            {result ? (
              <motion.div key="report" initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="space-y-6 flex-1">
                <div className={`backdrop-blur-md border p-5 rounded-2xl flex items-start gap-4 shadow-inner ${
                  result.confidence > 0.7 ? 'bg-red-500/20 border-red-400/50' : 
                  result.confidence > 0.4 ? 'bg-orange-500/20 border-orange-400/50' : 
                  'bg-green-500/20 border-green-400/50'
                }`}>
                  {result.confidence > 0.4 ? (
                    <AlertTriangle className={`w-8 h-8 shrink-0 mt-1 ${
                      result.confidence > 0.7 ? 'text-red-400' : 'text-orange-400'
                    }`} />
                  ) : (
                    <CheckCircle className="w-8 h-8 text-green-400 shrink-0 mt-1" />
                  )}
                  <div>
                    <h3 className="font-bold text-white text-xl font-display tracking-wide drop-shadow-sm">
                      {result.disease_detected} 
                      <span className="opacity-80 text-sm font-sans">
                        ({Math.round(result.confidence * 100)}% Confidence)
                      </span>
                    </h3>
                    <p className={`text-sm mt-2 font-medium leading-relaxed ${
                      result.confidence > 0.7 ? 'text-red-100' : 
                      result.confidence > 0.4 ? 'text-orange-100' : 'text-green-100'
                    }`}>
                      Analysis completed using OpenAI Vision API with agricultural expertise.
                    </p>
                  </div>
                </div>

                <div className="mt-8">
                  <h4 className="font-bold text-white mb-4 tracking-wide font-display text-lg">AI Recommendations</h4>
                  <div className="bg-white/10 p-5 rounded-xl shadow-sm border border-white/10 backdrop-blur-sm">
                    <p className="text-white/90 text-sm font-medium leading-relaxed">
                      {result.recommendation}
                    </p>
                  </div>
                </div>
              </motion.div>
            ) : (
              <motion.div key="empty" initial={{ opacity: 0 }} animate={{ opacity: 1 }} className="flex-1 flex flex-col items-center justify-center opacity-60 space-y-5">
                <Search className="w-20 h-20 text-white/50 drop-shadow-sm" />
                <p className="text-white font-medium text-center max-w-sm leading-relaxed tracking-wide">Awaiting input... Upload a crop or soil image to engage our OpenAI Vision API analysis.</p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
