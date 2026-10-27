import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send } from 'lucide-react';

// Knowledge base for Rakhi
const RAKHI_KNOWLEDGE_BASE = {
  'file a missing person report': 'To file a missing person report, go to **File Intake Report** tab. Click "Report Missing Person", fill in details like name, age, photo, marks, and location last seen. Press Submit. Your report goes to all 4 districts immediately! 📍',
  'match review': 'The **Match Review** tab shows AI-found candidates for missing cases. Each match has a "Fused Score" combining face recognition (35%), name similarity (25%), physical attributes (20%), and location/time feasibility (20%). Review and verify or reject matches.',
  'audit trail': 'The **Audit Trail** is an immutable record of every action in Rakshak Link - who accessed what, when, and why. It uses SHA-256 hash-chain technology to detect any tampering. Essential for compliance! 🔐',
  'dashboard': 'The **Dashboard** shows live stats: open cases, probable matches, verified links, trafficking syndicates detected, and match accuracy (Precision@5). Click metric cards to dive deeper! 📊',
  'case directory': 'The **Case Directory** lets you browse all missing/found person reports across Pune, Mumbai Suburban, Thane, and Nagpur. Filter by district, case type, or search by name. 🔍',
  'trafficking graph': 'The **Trafficking Graph** visualizes criminal networks. Nodes are cases, edges connect shared phone numbers or locations. Syndicates (3+ linked cases) are flagged in red. Powered by NetworkX! 🕸️',
  'how does matching work': 'Rakshak Link uses InsightFace AI (512-dimensional face embeddings) + name phonetics + physical attributes + geography/time. All signals fuse into a single score. No single metric dominates—holistic matching! 🧠',
  'what is insightface': 'InsightFace is a deep learning model that converts faces to 512-dimensional vectors. Same person = vectors close together. Different person = vectors far apart. We compare vectors to find matches! 👤',
  'who can verify matches': 'Only **Investigating Officers** and **CWC Officers** can verify matches across districts. Station Officers can view but not verify (security safeguard). Once verified, both districts get an alert! 🚨',
  'default': 'Hi! I\'m Rakhi, your AI guide. 🤖 Ask me about: Dashboard, Case Directory, File Intake Report, Match Review, Trafficking Graph, Audit Trail, or how matching works! What would you like to know? 💭'
};

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

  const findAnswer = (question) => {
    const q = question.toLowerCase().trim();
    
    // Exact match
    if (RAKHI_KNOWLEDGE_BASE[q]) {
      return RAKHI_KNOWLEDGE_BASE[q];
    }
    
    // Partial match
    for (const [key, answer] of Object.entries(RAKHI_KNOWLEDGE_BASE)) {
      if (key !== 'default' && (q.includes(key) || key.includes(q))) {
        return answer;
      }
    }
    
    // Try with keywords
    const keywords = {
      'file|report|missing': RAKHI_KNOWLEDGE_BASE['file a missing person report'],
      'match|review|score': RAKHI_KNOWLEDGE_BASE['match review'],
      'audit|trail|log': RAKHI_KNOWLEDGE_BASE['audit trail'],
      'dashboard|stat|metric': RAKHI_KNOWLEDGE_BASE['dashboard'],
      'case|directory|browse': RAKHI_KNOWLEDGE_BASE['case directory'],
      'graph|network|syndicate': RAKHI_KNOWLEDGE_BASE['trafficking graph'],
      'face|ai|embedding|insightface': RAKHI_KNOWLEDGE_BASE['what is insightface'],
      'verify|io|officer': RAKHI_KNOWLEDGE_BASE['who can verify matches'],
    };
    
    for (const [pattern, answer] of Object.entries(keywords)) {
      const regex = new RegExp(pattern, 'i');
      if (regex.test(q)) {
        return answer;
      }
    }
    
    return RAKHI_KNOWLEDGE_BASE['default'];
  };

  const sendMessage = () => {
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

    // Simulate thinking time
    setTimeout(() => {
      const answer = findAnswer(input);
      const rakhiMsg = {
        id: messages.length + 2,
        sender: 'rakhi',
        text: answer,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, rakhiMsg]);
      setLoading(false);
    }, 800);
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
