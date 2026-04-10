import { motion, AnimatePresence } from 'framer-motion';
import { MessageSquare, ThumbsUp, MapPin, Hash, Send } from 'lucide-react';
import { useState, useEffect } from 'react';

interface Comment {
  id: string;
  author: string;
  content: string;
  time: string;
}

interface Post {
  id: string;
  author: string;
  location: string;
  time: string;
  content: string;
  likes: number;
  comments: number;
  active: boolean;
  comment_list: Comment[];
}

export default function Community() {
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [newPostContent, setNewPostContent] = useState('');
  const [posting, setPosting] = useState(false);
  
  // State for comments
  const [expandedComments, setExpandedComments] = useState<string | null>(null);
  const [newCommentContent, setNewCommentContent] = useState('');

  useEffect(() => {
    fetchPosts();
  }, []);

  const fetchPosts = async () => {
    try {
      const response = await fetch('/api/posts');
      if (response.ok) {
        const data = await response.json();
        setPosts(data);
      }
    } catch (err) {
      console.error("Failed to fetch posts:", err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreatePost = async () => {
    if (!newPostContent.trim() || posting) return;
    setPosting(true);
    try {
      const response = await fetch('/api/posts', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          author: 'AgriBlast User',
          location: 'Local Region',
          content: newPostContent,
          time: 'Just now'
        })
      });
      if (response.ok) {
        setNewPostContent('');
        fetchPosts();
      }
    } catch (err) {
      console.error("Failed to create post:", err);
    } finally {
      setPosting(false);
    }
  };

  const handleLike = async (postId: string) => {
    try {
      // Optimistic update
      setPosts(posts.map(p => p.id === postId ? { ...p, likes: p.likes + 1 } : p));
      
      const response = await fetch(`/api/posts/${postId}/like`, {
        method: 'POST'
      });
      
      if (!response.ok) {
        // Revert on failure
        fetchPosts();
      }
    } catch (err) {
      console.error("Failed to like post:", err);
      fetchPosts();
    }
  };

  const handleComment = async (postId: string) => {
    if (!newCommentContent.trim()) return;
    try {
      const response = await fetch(`/api/posts/${postId}/comment`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          author: 'AgriBlast User',
          content: newCommentContent,
          time: 'Just now'
        })
      });
      if (response.ok) {
        setNewCommentContent('');
        fetchPosts();
      }
    } catch (err) {
      console.error("Failed to post comment:", err);
    }
  };

  return (
    <div className="space-y-8 max-w-7xl mx-auto">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
        <div>
          <h1 className="text-4xl font-black text-white drop-shadow-lg tracking-wide font-display">Local Farm Network</h1>
          <p className="text-white/80 font-medium mt-2 tracking-wide">Connect, share, and solve problems with farmers in your region.</p>
        </div>
        <motion.div whileHover={{ scale: 1.05 }} className="glass-panel text-white border-white/20 px-5 py-3 rounded-2xl flex items-center gap-3 shadow-lg bg-black/40 cursor-pointer">
          <div className="flex -space-x-3">
             <div className="w-8 h-8 rounded-full bg-slate-300 border-2 border-slate-900 shadow-sm relative z-20"></div>
             <div className="w-8 h-8 rounded-full bg-slate-400 border-2 border-slate-900 shadow-sm relative z-10"></div>
             <div className="w-8 h-8 rounded-full bg-slate-500 border-2 border-slate-900 shadow-sm relative z-0"></div>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2.5 h-2.5 bg-nature-400 rounded-full animate-pulse shadow-[0_0_8px_rgba(74,222,128,0.8)]"></span>
            <span className="font-bold tracking-wide">Live</span>
          </div>
        </motion.div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          
          {/* Create Post Interface */}
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} className="glass-panel p-6 flex gap-5 items-start shadow-xl bg-slate-900/60 mb-8 border-white/10">
             <div className="w-14 h-14 bg-gradient-to-tr from-sun-400 to-nature-500 rounded-full flex shrink-0 shadow-inner border border-white/20 relative overflow-hidden">
                <img src="/background.png" className="opacity-40 object-cover" alt="" />
             </div>
             <div className="flex-1">
               <textarea 
                 value={newPostContent}
                 onChange={(e) => setNewPostContent(e.target.value)}
                 className="w-full bg-white/5 backdrop-blur-md border border-white/10 rounded-2xl p-4 text-white outline-none focus:bg-white/10 focus:border-nature-400 focus:ring-1 focus:ring-nature-400 placeholder:text-white/40 transition-all font-medium resize-none shadow-inner" 
                 rows={3} 
                 placeholder="Share agricultural insights or ask for regional help..."
               />
               <div className="flex justify-between items-center mt-4">
                 <div className="flex gap-2 text-white/50">
                    <button className="p-2 hover:bg-white/10 rounded-full transition-colors"><MapPin size={20}/></button>
                    <button className="p-2 hover:bg-white/10 rounded-full transition-colors"><Hash size={20}/></button>
                 </div>
                 <motion.button 
                   onClick={handleCreatePost}
                   disabled={posting || !newPostContent.trim()}
                   whileHover={{ scale: 1.05 }} 
                   whileTap={{ scale: 0.95 }} 
                   className="bg-nature-500 hover:bg-nature-400 disabled:opacity-50 text-white px-8 py-2.5 rounded-full font-bold shadow-[0_0_15px_rgba(34,197,94,0.4)] transition-all"
                 >
                   {posting ? 'Publishing...' : 'Publish'}
                 </motion.button>
               </div>
             </div>
          </motion.div>

          {/* Feed */}
          {loading ? (
             <div className="w-full py-10 flex justify-center">
                 <div className="w-10 h-10 border-4 border-nature-400 border-t-transparent rounded-full animate-spin"></div>
             </div>
          ) : posts.length === 0 ? (
             <div className="glass-panel p-10 text-center text-white/50">No posts yet. Be the first to share!</div>
          ) : (
            posts.map((post, idx) => (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.05 * idx }}
                key={post.id} 
                className="glass-panel p-7 shadow-lg bg-black/30 hover:bg-black/40 border-white/10 transition-colors"
              >
                <div className="flex items-center gap-4 mb-5">
                  <div className="w-12 h-12 bg-white/20 border border-white/30 rounded-full shadow-inner relative flex items-center justify-center font-bold text-white uppercase">
                      {post.author.charAt(0)}
                      {post.active && <span className="absolute bottom-0 right-0 w-3 h-3 bg-nature-400 border-2 border-slate-900 rounded-full"></span>}
                  </div>
                  <div>
                    <h4 className="font-bold text-white leading-tight font-display text-lg drop-shadow-sm">{post.author}</h4>
                    <p className="text-xs text-white/60 font-medium flex items-center gap-1.5 mt-0.5 tracking-wide"><MapPin size={12}/> {post.location} <span className="mx-1">•</span> {post.time}</p>
                  </div>
                </div>
                <p className="text-white/90 mb-6 leading-relaxed font-medium whitespace-pre-wrap">{post.content}</p>
                
                <div className="flex gap-8 border-t border-white/10 pt-4 text-white/60 font-semibold tracking-wide">
                  <motion.button 
                    onClick={() => handleLike(post.id)}
                    whileHover={{ y: -2 }} 
                    className="flex items-center gap-2 hover:text-nature-400 transition-colors group"
                  >
                    <span className="p-2 rounded-full group-hover:bg-nature-500/20 transition-colors"><ThumbsUp size={18}/></span> {post.likes}
                  </motion.button>
                  <motion.button 
                    onClick={() => setExpandedComments(expandedComments === post.id ? null : post.id)}
                    whileHover={{ y: -2 }} 
                    className="flex items-center gap-2 hover:text-blue-400 transition-colors group"
                  >
                    <span className="p-2 rounded-full group-hover:bg-blue-500/20 transition-colors"><MessageSquare size={18}/></span> {post.comments}
                  </motion.button>
                </div>

                {/* Comments Section */}
                <AnimatePresence>
                  {expandedComments === post.id && (
                    <motion.div 
                      initial={{ opacity: 0, height: 0 }} 
                      animate={{ opacity: 1, height: 'auto' }} 
                      exit={{ opacity: 0, height: 0 }}
                      className="mt-6 pt-4 border-t border-white/10 overflow-hidden"
                    >
                      <div className="space-y-4 mb-4 max-h-60 overflow-y-auto pr-2 custom-scrollbar">
                        {post.comment_list && post.comment_list.length > 0 ? (
                           post.comment_list.map(comment => (
                             <div key={comment.id} className="bg-white/5 rounded-xl p-4 border border-white/5">
                                <div className="flex justify-between items-start mb-1">
                                  <span className="font-bold text-sm text-white/80">{comment.author}</span>
                                  <span className="text-xs text-white/40">{comment.time}</span>
                                </div>
                                <p className="text-white/70 text-sm">{comment.content}</p>
                             </div>
                           ))
                        ) : (
                           <p className="text-white/40 text-sm text-center py-2">No comments yet.</p>
                        )}
                      </div>
                      
                      <div className="flex gap-2 relative items-center mt-2">
                        <input 
                          type="text" 
                          value={newCommentContent}
                          onChange={(e) => setNewCommentContent(e.target.value)}
                          onKeyPress={(e) => { if (e.key === 'Enter') handleComment(post.id); }}
                          placeholder="Write a comment..."
                          className="flex-1 bg-white/10 border border-white/20 text-white focus:bg-white/20 focus:border-blue-400 focus:ring-1 focus:ring-blue-400 rounded-full px-5 py-2.5 outline-none text-sm transition-all placeholder:text-white/40"
                        />
                        <button 
                          onClick={() => handleComment(post.id)}
                          disabled={!newCommentContent.trim()}
                          className="bg-blue-500 hover:bg-blue-400 disabled:opacity-50 text-white p-2.5 rounded-full transition-all"
                        >
                          <Send size={16} className="-ml-0.5 mt-0.5" />
                        </button>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </motion.div>
            ))
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} className="glass-panel p-6 shadow-xl bg-slate-900/60 border-white/10">
            <h3 className="font-bold text-white mb-5 border-b border-white/10 pb-3 font-display tracking-wider uppercase text-sm">Trending Hash-Tags</h3>
            <ul className="space-y-4">
              {['#WinterWheatHarvest', '#SoybeanAphids', '#IrrigationSchedules', '#DroughtPrep'].map((tag) => (
                 <li key={tag} className="text-nature-300 font-bold hover:text-nature-200 cursor-pointer transition-colors flex items-center gap-2 tracking-wide text-sm">
                    <Hash size={14}/> {tag.substring(1)}
                 </li>
              ))}
            </ul>
          </motion.div>
          
          <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.1 }} className="glass-panel p-6 shadow-xl bg-gradient-to-br from-sun-500/30 to-sun-700/30 border border-sun-400/40 relative overflow-hidden">
            <div className="absolute top-0 right-0 w-32 h-32 bg-sun-400 opacity-20 rounded-full blur-2xl"></div>
            <div className="relative z-10">
              <h3 className="font-bold text-sun-100 mb-3 font-display tracking-widest uppercase text-xs flex items-center gap-2"><div className="w-2 h-2 rounded-full bg-sun-300 animate-pulse"></div> Market Alert</h3>
              <p className="text-white text-md font-medium leading-relaxed drop-shadow-sm">Corn prices surged 2% this morning due to regional drought concerns across the midwest sector.</p>
              <button className="mt-4 text-xs font-bold text-sun-200 uppercase tracking-wider hover:text-white transition-colors">Read Report &rarr;</button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
