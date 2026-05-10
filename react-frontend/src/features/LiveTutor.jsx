import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Bot, User, Send, Loader2, X } from 'lucide-react';

const API = `http://${window.location.hostname}:8000`;

export function LiveTutor({ moduleId, token, onClose }) {
  const [messages, setMessages] = useState([{ role: 'model', content: "Hi! I'm your AI tutor. Ask me anything about this module." }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isLoading]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const newMsg = { role: 'user', content: input };
    const newMessages = [...messages, newMsg];
    setMessages(newMessages);
    setInput('');
    setIsLoading(true);

    try {
      // the backend uses 'user' and 'model'
      const payload = { messages: newMessages.map(m => ({ role: m.role, content: m.content })) };
      const res = await fetch(`${API}/modules/${moduleId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(payload),
      });

      if (!res.ok) throw new Error('Network error');
      const data = await res.json();
      setMessages([...newMessages, { role: 'model', content: data.response }]);
    } catch (err) {
      setMessages([...newMessages, { role: 'model', content: "Sorry, I couldn't reach the server." }]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <motion.div 
      initial={{ x: '100%' }} 
      animate={{ x: 0 }} 
      exit={{ x: '100%' }}
      transition={{ type: 'spring', damping: 25, stiffness: 200 }}
      className="fixed right-0 top-0 bottom-0 w-[400px] z-[100] glass-card bg-surface/90 backdrop-blur-3xl border-l border-white/10 flex flex-col shadow-2xl shadow-blue-glow/20"
    >
      <div className="p-4 border-b border-white/10 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Bot className="w-5 h-5 text-cyan" />
          <h3 className="font-display font-bold text-lg">Live Tutor</h3>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-white/10 rounded-[2px] transition-colors text-slate-400 hover:text-white">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar">
        {messages.map((msg, idx) => (
          <div key={idx} className={`flex gap-3 ${msg.role === 'user' ? 'flex-row-reverse' : ''}`}>
            <div className={`w-8 h-8 rounded-[2px] flex items-center justify-center flex-shrink-0 ${msg.role === 'user' ? 'bg-cyan/20 text-cyan' : 'bg-cyan/20 text-cyan'}`}>
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4" />}
            </div>
            <div className={`max-w-[80%] rounded-[2px] p-4 ${msg.role === 'user' ? 'bg-cyan text-black rounded-tr-none' : 'bg-white/5 border border-white/10 text-slate-200 rounded-tl-none'}`}>
              {msg.role === 'user' ? (
                <p className="text-sm">{msg.content}</p>
              ) : (
                <div className="prose prose-invert prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      code({node, inline, className, children, ...props}) {
                        const match = /language-(\w+)/.exec(className || '')
                        return !inline && match ? (
                          <SyntaxHighlighter style={vscDarkPlus} language={match[1]} PreTag="div" {...props}>
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        ) : (
                          <code className="bg-black/30 px-1 py-0.5 rounded text-cyan text-xs" {...props}>
                            {children}
                          </code>
                        )
                      }
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div className="flex gap-3">
             <div className="w-8 h-8 rounded-[2px] flex items-center justify-center bg-cyan/20 text-cyan">
               <Bot className="w-4 h-4" />
             </div>
             <div className="bg-white/5 border border-white/10 rounded-[2px] rounded-tl-none p-4 flex items-center gap-2">
               <Loader2 className="w-4 h-4 text-cyan animate-spin" />
               <span className="text-xs text-slate-400 font-mono">Thinking...</span>
             </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-white/10 bg-black/20">
        <form onSubmit={handleSubmit} className="relative">
          <input 
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about this module..."
            className="w-full bg-white/5 border border-white/10 rounded-[2px] pl-4 pr-12 py-3 text-sm focus:outline-none focus:border-cyan/50 focus:ring-1 focus:ring-cyan/50 transition-all text-white placeholder-slate-500"
          />
          <button 
            type="submit" 
            disabled={!input.trim() || isLoading}
            className="absolute right-2 top-1/2 -translate-y-1/2 w-8 h-8 bg-cyan text-black rounded-[2px] flex items-center justify-center disabled:opacity-50 hover:scale-105 transition-all"
          >
            <Send className="w-3 h-3" />
          </button>
        </form>
      </div>
    </motion.div>
  );
}
