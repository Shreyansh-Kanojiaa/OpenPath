import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Send, Loader2, X } from 'lucide-react';

const API = import.meta.env.VITE_API_URL || `http://${window.location.hostname}:8000`;

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
      className="fixed right-0 top-0 bottom-0 w-full sm:w-[400px] max-w-full z-[100] glass-card bg-surface border-l border-border flex flex-col rounded-none"
    >
      <div className="p-5 pt-24 sm:pt-5 border-b border-border flex justify-between items-center">
        <div className="flex items-center gap-2">
          <span className="w-1.5 h-1.5 rounded-full bg-accent" />
          <h3 className="font-mono text-[11px] uppercase tracking-[0.2em] text-text-secondary">OpenPath Tutor</h3>
        </div>
        <button onClick={onClose} className="p-2 hover:bg-overlay rounded-full transition-colors text-text-secondary hover:text-text-primary">
          <X className="w-4 h-4" />
        </button>
      </div>

      <div className="flex-1 overflow-y-auto p-5 space-y-6 custom-scrollbar">
        {messages.map((msg, idx) => (
          msg.role === 'user' ? (
            <div key={idx} className="flex justify-end">
              <div className="max-w-[85%] rounded-2xl rounded-tr-sm px-4 py-3 bg-accent/15 border border-accent/30 text-text-primary text-sm">
                {msg.content}
              </div>
            </div>
          ) : (
            <div key={idx} className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-accent/60" />
                <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-text-muted">OpenPath Tutor</span>
              </div>
              <div className="rounded-2xl rounded-tl-sm px-4 py-3 bg-subtle border border-border text-text-primary">
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
                          <code className="bg-base px-1 py-0.5 rounded text-accent text-xs" {...props}>
                            {children}
                          </code>
                        )
                      }
                    }}
                  >
                    {msg.content}
                  </ReactMarkdown>
                </div>
              </div>
            </div>
          )
        ))}
        {isLoading && (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="w-1.5 h-1.5 rounded-full bg-accent/60" />
              <span className="font-mono text-[10px] uppercase tracking-[0.2em] text-text-muted">OpenPath Tutor</span>
            </div>
            <div className="bg-subtle border border-border rounded-2xl rounded-tl-sm p-4 flex items-center gap-2 w-fit">
              <Loader2 className="w-4 h-4 text-text-secondary animate-spin" />
              <span className="text-sm text-text-secondary">Thinking…</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      <div className="p-4 border-t border-border bg-base">
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder="Ask about anything in this lesson…"
            className="w-full bg-subtle border border-border rounded-full pl-5 pr-12 py-3 text-sm focus:outline-none focus:border-accent transition-colors text-text-primary placeholder:text-text-muted"
          />
          <button
            type="submit"
            disabled={!input.trim() || isLoading}
            className="absolute right-1.5 top-1/2 -translate-y-1/2 w-8 h-8 bg-accent text-charcoal-900 rounded-full flex items-center justify-center disabled:opacity-50 hover:bg-blue-bright transition-all duration-200"
          >
            <Send className="w-3.5 h-3.5" />
          </button>
        </form>
      </div>
    </motion.div>
  );
}
