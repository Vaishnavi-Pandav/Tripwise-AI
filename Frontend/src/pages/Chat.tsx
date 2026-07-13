import { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Send, Bot, User, Sparkles, RotateCcw, Copy, Check } from 'lucide-react';
import Navbar from '../components/Navbar';
import { aiChat } from '../services/api';
import { useAuth } from '../context/AuthContext';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const SUGGESTIONS = [
  "Plan a 5-day Goa trip under ₹15,000 for 2 people",
  "Best time to visit Manali for snow",
  "Budget breakdown for Kerala backwater trip",
  "Hidden gems near Jaipur",
  "Compare Goa vs Gokarna for couples",
  "What to pack for a Ladakh trip in July?",
];

const renderMessage = (text: string) => {
  const lines = text.split('\n');
  return lines.map((line, i) => {
    if (line.startsWith('## ')) return <h3 key={i} className="text-base font-bold text-white mt-3 mb-1">{line.replace('## ','')}</h3>;
    if (line.startsWith('### ')) return <h4 key={i} className="text-sm font-semibold text-emerald-400 mt-2 mb-1">{line.replace('### ','')}</h4>;
    if (line.startsWith('**') && line.endsWith('**')) return <p key={i} className="font-semibold text-white/90 text-sm">{line.replace(/\*\*/g,'')}</p>;
    if (line.match(/^[-*] /)) return (
      <div key={i} className="flex items-start gap-2 text-white/80 text-sm py-0.5">
        <span className="mt-1.5 w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0" />
        <span dangerouslySetInnerHTML={{ __html: line.replace(/^[-*] /,'').replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>') }} />
      </div>
    );
    if (line.trim() === '') return <div key={i} className="h-1" />;
    return <p key={i} className="text-white/80 text-sm leading-relaxed" dangerouslySetInnerHTML={{ __html: line.replace(/\*\*(.+?)\*\*/g,'<strong>$1</strong>') }} />;
  });
};

export default function Chat() {
  const [darkMode, setDarkMode] = useState(true);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: "Hi! I'm **TripWise AI**, your personal travel planning assistant. 🌍\n\nAsk me anything about:\n- Planning trips and itineraries\n- Budget estimates and cost breakdowns\n- Best destinations and hidden gems\n- Hotel and package recommendations\n- Weather and travel tips\n\nHow can I help you plan your next adventure?",
      timestamp: new Date(),
    }
  ]);
  const [input, setInput]       = useState('');
  const [loading, setLoading]   = useState(false);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [cooldown, setCooldown] = useState(0);
  const bottomRef               = useRef<HTMLDivElement>(null);
  const inputRef                = useRef<HTMLTextAreaElement>(null);
  const { user } = useAuth();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  useEffect(() => {
    if (cooldown > 0) {
      const timer = setTimeout(() => setCooldown(cooldown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [cooldown]);

  const sendMessage = async (text: string) => {
    if (!text.trim() || loading || cooldown > 0) return;
    const userMsg: Message = { id: Date.now().toString(), role: 'user', content: text.trim(), timestamp: new Date() };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);
    setCooldown(3);
    try {
      const res = await aiChat(text.trim());
      const aiMsg: Message = { id: (Date.now()+1).toString(), role: 'assistant', content: res.reply, timestamp: new Date() };
      setMessages(prev => [...prev, aiMsg]);
    } catch (e: unknown) {
      let errMsg = "Sorry, I couldn't reach the AI service. Please try again in a moment.";
      if (e instanceof Error) {
        if (e.message.includes('429') || e.message.includes('rate'))
          errMsg = "Too many requests — please wait a few seconds and try again.";
        else if (e.message.includes('502') || e.message.includes('503'))
          errMsg = "AI service is temporarily unavailable. Please try again shortly.";
        else if (e.message.includes('Network') || e.message.includes('ERR_NETWORK'))
          errMsg = "Network error — please check your connection and try again.";
        else if (e.message.includes('timeout') || e.message.includes('ECONNABORTED'))
          errMsg = "Request timed out — the AI is taking too long. Please try again.";
      }
      setMessages(prev => [...prev, { id: (Date.now()+1).toString(), role: 'assistant', content: errMsg, timestamp: new Date() }]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(input); }
  };

  const copyMessage = (id: string, content: string) => {
    navigator.clipboard.writeText(content);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };

  const clearChat = () => setMessages([{
    id: '0', role: 'assistant',
    content: "Chat cleared! How can I help you plan your next trip? 🌍",
    timestamp: new Date(),
  }]);

  return (
    <div className={`min-h-screen flex flex-col ${darkMode ? 'bg-[#020817]' : 'bg-gray-50'}`}>
      <Navbar darkMode={darkMode} setDarkMode={setDarkMode} />

      <main className="flex-grow flex flex-col pt-20 pb-0">
        <div className="max-w-4xl mx-auto w-full flex-grow flex flex-col px-4 sm:px-6">

          {/* Header */}
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl flex items-center justify-center"
                style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                <Bot size={20} className="text-white" />
              </div>
              <div>
                <h1 className={`font-playfair font-bold text-lg ${darkMode?'text-white':'text-gray-900'}`}>TripWise AI Chat</h1>
                <div className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
                  <span className={`text-xs ${darkMode?'text-white/50':'text-gray-500'}`}>Online · Powered by Gemini</span>
                </div>
              </div>
            </div>
            <button onClick={clearChat}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded-xl text-xs font-medium transition-colors ${darkMode?'text-white/50 hover:text-white hover:bg-white/10':'text-gray-500 hover:text-gray-700 hover:bg-gray-100'}`}>
              <RotateCcw size={13} /> Clear chat
            </button>
          </div>

          {/* Messages */}
          <div className="flex-grow overflow-y-auto py-4 space-y-4" style={{ minHeight:0 }}>

            {/* Suggestions (only when 1 message) */}
            {messages.length === 1 && (
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 mb-4">
                {SUGGESTIONS.map((s,i) => (
                  <motion.button key={i} initial={{ opacity:0, y:10 }} animate={{ opacity:1, y:0 }}
                    transition={{ delay: i * 0.05 }}
                    onClick={() => sendMessage(s)}
                    className={`text-left px-4 py-3 rounded-xl text-sm transition-all border ${darkMode?'bg-white/4 border-white/8 text-white/70 hover:bg-white/8 hover:text-white hover:border-emerald-500/30':'bg-white border-gray-200 text-gray-600 hover:border-emerald-400 hover:text-gray-900'}`}
                    style={{ background: darkMode ? 'rgba(255,255,255,0.04)' : 'white', border: darkMode ? '1px solid rgba(255,255,255,0.08)' : '1px solid #e5e7eb' }}>
                    <Sparkles size={13} className="text-emerald-400 inline mr-2" />
                    {s}
                  </motion.button>
                ))}
              </div>
            )}

            {messages.map((msg) => (
              <motion.div key={msg.id}
                initial={{ opacity:0, y:16 }} animate={{ opacity:1, y:0 }}
                transition={{ duration:0.3 }}
                className={`flex gap-3 ${msg.role==='user' ? 'justify-end' : 'justify-start'}`}>

                {/* AI avatar */}
                {msg.role === 'assistant' && (
                  <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-1"
                    style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                    <Bot size={15} className="text-white" />
                  </div>
                )}

                {/* Bubble */}
                <div className={`group relative max-w-[85%] sm:max-w-[75%] ${msg.role==='user' ? 'order-1' : ''}`}>
                  <div className={`px-4 py-3 rounded-2xl ${
                    msg.role === 'user'
                      ? 'text-white rounded-br-sm'
                      : darkMode ? 'rounded-bl-sm' : 'rounded-bl-sm shadow-sm'
                  }`}
                    style={msg.role === 'user'
                      ? { background:'linear-gradient(135deg,#10b981,#0ea5e9)' }
                      : darkMode
                        ? { background:'rgba(255,255,255,0.06)', border:'1px solid rgba(255,255,255,0.1)' }
                        : { background:'white', border:'1px solid #e5e7eb' }
                    }>
                    <div className={msg.role === 'user' ? 'text-white text-sm' : ''}>
                      {msg.role === 'assistant' ? renderMessage(msg.content) : <p className="text-sm">{msg.content}</p>}
                    </div>
                  </div>

                  {/* Copy button */}
                  {msg.role === 'assistant' && (
                    <button onClick={() => copyMessage(msg.id, msg.content)}
                      className="absolute -bottom-5 right-0 opacity-0 group-hover:opacity-100 transition-opacity flex items-center gap-1 text-xs text-white/30 hover:text-white/60">
                      {copiedId === msg.id ? <Check size={11} /> : <Copy size={11} />}
                      {copiedId === msg.id ? 'Copied' : 'Copy'}
                    </button>
                  )}

                  <p className={`text-[10px] mt-1 ${msg.role==='user' ? 'text-right text-white/50' : darkMode?'text-white/30':'text-gray-400'}`}>
                    {msg.timestamp.toLocaleTimeString('en-IN', { hour:'2-digit', minute:'2-digit' })}
                  </p>
                </div>

                {/* User avatar */}
                {msg.role === 'user' && (
                  <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center mt-1 order-2"
                    style={{ background:'rgba(255,255,255,0.1)' }}>
                    {user?.photoURL
                      ? <img src={user.photoURL} className="w-8 h-8 rounded-full object-cover" alt="you" />
                      : <User size={15} className={darkMode?'text-white':'text-gray-500'} />
                    }
                  </div>
                )}
              </motion.div>
            ))}

            {/* Typing indicator */}
            {loading && (
              <motion.div initial={{ opacity:0 }} animate={{ opacity:1 }} className="flex gap-3">
                <div className="w-8 h-8 rounded-full flex-shrink-0 flex items-center justify-center"
                  style={{ background:'linear-gradient(135deg,#10b981,#0ea5e9)' }}>
                  <Bot size={15} className="text-white" />
                </div>
                <div className="px-4 py-3 rounded-2xl rounded-bl-sm flex items-center gap-1.5"
                  style={{ background: darkMode ? 'rgba(255,255,255,0.06)' : 'white', border: darkMode ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e5e7eb' }}>
                  {[0,1,2].map(i => (
                    <span key={i} className="w-2 h-2 rounded-full bg-emerald-400 animate-bounce"
                      style={{ animationDelay:`${i*150}ms` }} />
                  ))}
                </div>
              </motion.div>
            )}

            <div ref={bottomRef} />
          </div>

          {/* Input */}
          <div className={`py-4 border-t ${darkMode?'border-white/8':'border-gray-200'}`}
            style={{ borderTop: darkMode ? '1px solid rgba(255,255,255,0.08)' : '1px solid #e5e7eb' }}>
            <div className="flex items-end gap-3">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={e => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask anything about travel…"
                  rows={1}
                  className={`w-full resize-none rounded-2xl px-4 py-3 text-sm outline-none transition-all pr-4 ${darkMode?'text-white placeholder:text-white/30':'text-gray-900 placeholder:text-gray-400'}`}
                  style={{
                    background: darkMode ? 'rgba(255,255,255,0.06)' : 'white',
                    border: darkMode ? '1px solid rgba(255,255,255,0.1)' : '1px solid #e5e7eb',
                    maxHeight:'120px', overflowY:'auto',
                  }}
                  onInput={e => {
                    const t = e.target as HTMLTextAreaElement;
                    t.style.height = 'auto';
                    t.style.height = Math.min(t.scrollHeight, 120) + 'px';
                  }}
                />
              </div>
              <motion.button
                whileHover={input.trim() && !loading && cooldown === 0 ? { scale:1.05 } : {}}
                whileTap={input.trim() && !loading && cooldown === 0 ? { scale:0.95 } : {}}
                onClick={() => sendMessage(input)}
                disabled={!input.trim() || loading || cooldown > 0}
                className="w-11 h-11 rounded-xl flex items-center justify-center flex-shrink-0 transition-all disabled:opacity-40"
                style={{ background: input.trim() && !loading && cooldown === 0 ? 'linear-gradient(135deg,#10b981,#0ea5e9)' : 'rgba(255,255,255,0.08)' }}>
                {cooldown > 0 ? (
                  <span className="text-white text-xs font-medium">{cooldown}s</span>
                ) : (
                  <Send size={18} className="text-white" />
                )}
              </motion.button>
            </div>
            <p className={`text-xs mt-2 text-center ${darkMode?'text-white/20':'text-gray-400'}`}>
              TripWise AI can make mistakes. Verify important travel information.
            </p>
          </div>
        </div>
      </main>
    </div>
  );
}
