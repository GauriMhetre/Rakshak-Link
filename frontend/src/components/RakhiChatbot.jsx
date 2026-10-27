import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';

export default function RakhiChatbot() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      sender: 'rakhi',
      text: 'Hi! 👋 I\'m Rakhi, your AI assistant. I\'m here to help you navigate Rakshak Link. What would you like to know?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    // Add user message
    const userMsg = {
      id: messages.length + 1,
      sender: 'user',
      text: input,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      // Call Perplexity API
      const apiKey = import.meta.env.VITE_PERPLEXITY_API_KEY;
      if (!apiKey) {
        throw new Error('API key not configured');
      }

      const response = await fetch('https://api.perplexity.ai/chat/completions', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${apiKey}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          model: 'llama-2-7b-chat',
          messages: [
            {
              role: 'system',
              content: `You are Rakhi, a cute and helpful AI assistant for Rakshak Link - a cross-district missing person and anti-trafficking intelligence portal. 
              
Your role is to help users understand and navigate the application. Be friendly, concise, and always relate your answers back to how the app works.

Key features to mention when relevant:
- Dashboard: View case statistics, probable matches, and trafficking syndicates
- Case Directory: Browse and search missing/found person cases across 4 districts (Pune, Mumbai, Thane, Nagpur)
- File Intake Report: Report new missing or found persons
- Match Review: Evaluate multi-signal candidate matches (face, name, attributes, location/time)
- Trafficking Graph: View trafficking network clusters and phone number connections
- Audit Trail: Immutable record of all system actions for compliance

Keep responses helpful, supportive, and under 150 words. Use emojis occasionally to be cute and friendly.`
            },
            ...messages.map(msg => ({
              role: msg.sender === 'user' ? 'user' : 'assistant',
              content: msg.text
            })),
            { role: 'user', content: input }
          ],
          max_tokens: 200,
          temperature: 0.7,
        })
      });

      const data = await response.json();
      
      if (data.choices && data.choices[0]?.message?.content) {
        const rakhiMsg = {
          id: messages.length + 2,
          sender: 'rakhi',
          text: data.choices[0].message.content,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, rakhiMsg]);
      } else {
        throw new Error('No response from API');
      }
    } catch (err) {
      console.error('Chatbot error:', err);
      const errorMsg = {
        id: messages.length + 2,
        sender: 'rakhi',
        text: 'Oops! I hit a little snag. 😅 Try asking me something about the app, like "How do I file a missing person report?" or "What does the Match Review tab do?"',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-40">
      {/* Chat Window */}
      {isOpen && (
        <div className="absolute bottom-20 right-0 w-96 h-96 bg-darkblue border border-earth/30 rounded-3xl shadow-2xl flex flex-col overflow-hidden glass-card">
          {/* Header */}
          <div className="bg-gradient-to-r from-darkblue to-darkblue/80 border-b border-earth/20 px-5 py-4 flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <div className="w-3 h-3 bg-earth rounded-full animate-pulse"></div>
              <h3 className="font-bold text-ashgray">Rakhi 🤖</h3>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="text-ashgray/70 hover:text-ashgray transition-colors"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto px-4 py-4 space-y-3 bg-darkblue/40">
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`flex ${msg.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-xs px-4 py-2 rounded-2xl text-sm ${
                    msg.sender === 'user'
                      ? 'bg-earth text-darkblue font-semibold'
                      : 'bg-darkblue/60 text-ashgray border border-earth/20'
                  }`}
                >
                  {msg.text}
                </div>
              </div>
            ))}
            {loading && (
              <div className="flex justify-start">
                <div className="bg-darkblue/60 text-ashgray px-4 py-2 rounded-2xl border border-earth/20">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-earth rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-earth rounded-full animate-bounce delay-100"></div>
                    <div className="w-2 h-2 bg-earth rounded-full animate-bounce delay-200"></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="border-t border-earth/20 px-4 py-3 bg-darkblue/60 flex space-x-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
              placeholder="Ask me anything..."
              className="flex-1 bg-darkblue/40 text-ashgray placeholder-ashgray/50 px-3 py-2 rounded-full text-sm focus:outline-none border border-earth/20 focus:border-earth/50 transition-all"
              disabled={loading}
            />
            <button
              onClick={sendMessage}
              disabled={loading || !input.trim()}
              className="bg-earth hover:bg-earth/90 text-darkblue p-2 rounded-full transition-all disabled:opacity-50"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}

      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-16 h-16 bg-gradient-to-r from-earth to-earth/80 hover:from-earth/90 hover:to-earth text-darkblue rounded-full shadow-lg flex items-center justify-center transition-all hover:scale-110 active:scale-95"
      >
        {isOpen ? (
          <X className="w-7 h-7" />
        ) : (
          <MessageCircle className="w-7 h-7" />
        )}
      </button>
    </div>
  );
}
