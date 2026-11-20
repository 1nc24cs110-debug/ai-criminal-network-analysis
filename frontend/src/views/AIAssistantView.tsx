import React, { useState } from 'react';
import {
  BotMessageSquare, Send, Sparkles, FileText, ShieldAlert,
  ChevronRight, ArrowRight, CornerDownRight, CheckCircle2, AlertCircle
} from 'lucide-react';
import { api } from '../api';

interface Message {
  id: string;
  sender: 'USER' | 'ASSISTANT';
  text: string;
  citations?: Array<{ document_title: string; excerpt: string; page: number; confidence: number }>;
  followups?: string[];
  hasUnverified?: boolean;
  timestamp: string;
}

export const AIAssistantView: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      sender: 'ASSISTANT',
      text: (
        "Welcome to the AI Investigation Assistant. I analyze authorized case records, " +
        "trace cross-case nexus points, and evaluate evidence provenance.\n\n" +
        "Every finding I provide is strictly cited to primary documentary records. " +
        "Unverified AI extractions are explicitly flagged to preserve evidentiary integrity."
      ),
      citations: [],
      followups: [
        "Which relationships have not been verified?",
        "What entities connect Case CR-2026-0812 and CR-2026-0944?",
        "What evidence supports Dmitri Voronov?",
        "What changed in this network during March 2026?"
      ],
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    }
  ]);

  const [inputQuery, setInputQuery] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSend = async (queryToSend?: string) => {
    const q = (queryToSend || inputQuery).trim();
    if (!q) return;

    const userMsg: Message = {
      id: String(Date.now()),
      sender: 'USER',
      text: q,
      timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
    };

    setMessages((prev) => [...prev, userMsg]);
    setInputQuery('');
    setLoading(true);

    try {
      const res = await api.askAssistant(q);
      const assistantMsg: Message = {
        id: String(Date.now() + 1),
        sender: 'ASSISTANT',
        text: res.answer,
        citations: res.evidence_citations,
        followups: res.suggested_followups,
        hasUnverified: res.has_unverified_mentions,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, assistantMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: String(Date.now() + 1),
        sender: 'ASSISTANT',
        text: `Error processing investigative query: ${err.message}`,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
      };
      setMessages((prev) => [...prev, errorMsg]);
    } finally {
      setLoading(false);
    }
  };

  const smartQueries = [
    "Which relationships have not been verified?",
    "What entities connect Case CR-2026-0812 and CR-2026-0944?",
    "What evidence supports Dmitri Voronov?",
    "What evidence supports Klaus Richter?",
    "What changed in this network during March 2026?"
  ];

  return (
    <div className="h-[calc(100vh-4rem)] flex flex-col p-6 max-w-5xl mx-auto space-y-4">
      {/* Top Header */}
      <div className="pb-3 border-b border-slate-800 flex items-center justify-between shrink-0">
        <div className="flex items-center space-x-3">
          <div className="w-9 h-9 rounded-xl bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/20">
            <BotMessageSquare className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-base font-extrabold text-white tracking-wide">
              AI INVESTIGATION DECISION ASSISTANT
            </h1>
            <p className="text-[11px] text-slate-400 font-mono">
              EVIDENCE-GROUNDED NATURAL LANGUAGE REASONING // PROVENANCE CITATIONS
            </p>
          </div>
        </div>

        <span className="hidden sm:inline-block px-2.5 py-1 rounded-full bg-cyan-950 text-cyan-300 border border-cyan-800 font-mono text-[10px] font-bold">
          CITATIONS ENFORCED
        </span>
      </div>

      {/* Suggested Quick Prompt Chips */}
      <div className="flex items-center space-x-2 overflow-x-auto pb-1 shrink-0">
        <span className="text-[10px] font-mono text-slate-500 uppercase shrink-0 font-semibold">
          Recommended Queries:
        </span>
        {smartQueries.map((sq, i) => (
          <button
            key={i}
            onClick={() => handleSend(sq)}
            className="px-2.5 py-1 rounded-lg bg-slate-900/80 hover:bg-slate-800 border border-slate-800 hover:border-cyan-700/60 text-slate-300 hover:text-cyan-200 text-xs font-mono transition-all shrink-0"
          >
            {sq}
          </button>
        ))}
      </div>

      {/* Messages Stream Container */}
      <div className="flex-1 overflow-y-auto space-y-4 pr-1">
        {messages.map((m) => {
          const isUser = m.sender === 'USER';
          return (
            <div
              key={m.id}
              className={`flex flex-col ${isUser ? 'items-end' : 'items-start'} space-y-2`}
            >
              <div className="flex items-center space-x-2 text-[10px] font-mono text-slate-500 px-1">
                <span>{isUser ? 'INVESTIGATOR' : 'AI INTELLIGENCE ASSISTANT'}</span>
                <span>•</span>
                <span>{m.timestamp}</span>
              </div>

              <div
                className={`max-w-3xl p-4 rounded-2xl text-xs leading-relaxed ${
                  isUser
                    ? 'bg-cyan-900/50 text-cyan-50 border border-cyan-700/80 rounded-tr-none'
                    : 'bg-[#0D1527] text-slate-200 border border-slate-800 rounded-tl-none shadow-xl'
                }`}
              >
                <div className="whitespace-pre-wrap font-sans leading-relaxed">{m.text}</div>

                {/* Unverified Mentions Warning */}
                {m.hasUnverified && (
                  <div className="mt-3 p-2.5 rounded-lg bg-amber-950/60 border border-amber-800 text-amber-200 text-[11px] flex items-center space-x-2">
                    <ShieldAlert className="w-4 h-4 text-amber-400 shrink-0" />
                    <span>Contains unverified links requiring authorized investigator validation.</span>
                  </div>
                )}

                {/* Evidence Citations */}
                {m.citations && m.citations.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800 space-y-2">
                    <span className="text-[10px] font-mono uppercase tracking-wider text-cyan-400 font-bold block">
                      Supporting Primary Evidence Citations ({m.citations.length}):
                    </span>
                    <div className="space-y-1.5">
                      {m.citations.map((cite, cIdx) => (
                        <div
                          key={cIdx}
                          className="p-2.5 rounded-lg bg-slate-900/90 border border-slate-800 text-[11px] font-mono text-slate-300 space-y-1"
                        >
                          <div className="flex items-center justify-between text-cyan-300 font-semibold">
                            <span>📄 {cite.document_title} (Page {cite.page})</span>
                            <span className="text-[10px] text-slate-400">
                              Confidence: {Math.round(cite.confidence * 100)}%
                            </span>
                          </div>
                          <p className="text-slate-400 italic">"{cite.excerpt}"</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* Followup suggestions */}
                {m.followups && m.followups.length > 0 && (
                  <div className="mt-4 pt-3 border-t border-slate-800">
                    <span className="text-[10px] font-mono uppercase text-slate-500 font-semibold block mb-1.5">
                      Suggested Investigative Inquiries:
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {m.followups.map((f, fIdx) => (
                        <button
                          key={fIdx}
                          onClick={() => handleSend(f)}
                          className="px-2.5 py-1 rounded bg-slate-900 border border-slate-700/80 hover:border-cyan-600 text-cyan-300 hover:text-white text-[10px] font-mono flex items-center space-x-1 transition-all"
                        >
                          <span>{f}</span>
                          <ArrowRight className="w-3 h-3 text-cyan-400" />
                        </button>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          );
        })}

        {loading && (
          <div className="flex items-center space-x-2 text-cyan-400 font-mono text-xs p-3">
            <div className="w-4 h-4 border-2 border-cyan-400 border-t-transparent rounded-full animate-spin"></div>
            <span>Evaluating documentary citations & graph topology...</span>
          </div>
        )}
      </div>

      {/* Input Box */}
      <div className="shrink-0 pt-2 border-t border-slate-800">
        <form
          onSubmit={(e) => {
            e.preventDefault();
            handleSend();
          }}
          className="relative flex items-center"
        >
          <input
            type="text"
            value={inputQuery}
            onChange={(e) => setInputQuery(e.target.value)}
            placeholder="Ask an investigative question about cases, entities, unverified links, or evidence..."
            className="w-full pl-4 pr-24 py-3 bg-[#0D1527] border border-slate-700/80 rounded-xl text-slate-100 text-xs focus:border-cyan-500 focus:outline-none focus:ring-1 focus:ring-cyan-500 font-mono shadow-xl"
          />
          <button
            type="submit"
            disabled={loading || !inputQuery.trim()}
            className="absolute right-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white font-mono text-xs font-bold transition-all disabled:opacity-40 flex items-center space-x-1"
          >
            <span>Send</span>
            <Send className="w-3 h-3" />
          </button>
        </form>
        <p className="text-[10px] text-center text-slate-500 font-mono mt-2">
          Strict Evidence Provenance Safeguard: AI outputs cite verified case documents only. Never infers guilt.
        </p>
      </div>
    </div>
  );
};
