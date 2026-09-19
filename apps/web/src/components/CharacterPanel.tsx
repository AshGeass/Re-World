"use client";

import { useEffect, useState, useRef } from "react";
import { api, Character } from "@/lib/api";
import { useAppContext } from "./AppProvider";
import { Send, Loader2 } from "lucide-react";

export default function CharacterPanel() {
  const { storyId, branchId, currentSequence, selectedCharacterId, setSelectedCharacterId } = useAppContext();
  
  const [characters, setCharacters] = useState<Character[]>([]);
  const [character, setCharacter] = useState<Character | null>(null);
  
  const [chatLog, setChatLog] = useState<{role: 'user'|'character', content: string}[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [knowledgeCount, setKnowledgeCount] = useState(0);

  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (storyId) {
      api.getCharacters(storyId, branchId).then(setCharacters);
    }
  }, [storyId, branchId]);

  useEffect(() => {
    if (storyId && selectedCharacterId) {
      api.getCharacter(storyId, selectedCharacterId, branchId).then(setCharacter);
      // Reset chat when character changes
      setChatLog([]);
      
      // Fetch knowledge count for context
      api.getCharacterKnowledge(storyId, selectedCharacterId, currentSequence, branchId)
        .then(res => setKnowledgeCount(res.total))
        .catch(() => setKnowledgeCount(0));
    }
  }, [storyId, selectedCharacterId, branchId, currentSequence]);

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [chatLog]);

  const handleChat = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || !storyId || !selectedCharacterId) return;

    const userMsg = input;
    setInput("");
    setChatLog(prev => [...prev, { role: 'user', content: userMsg }]);
    setLoading(true);

    try {
      const res = await api.chatWithCharacter(storyId, selectedCharacterId, currentSequence, userMsg, branchId);
      setChatLog(prev => [...prev, { role: 'character', content: res.output }]);
      setKnowledgeCount(res.knowledge_count);
    } catch {
      setChatLog(prev => [...prev, { role: 'character', content: "Error: Could not communicate with character." }]);
    } finally {
      setLoading(false);
    }
  };

  if (!selectedCharacterId) {
    return (
      <div className="flex-1 flex flex-col border-b border-border p-4">
        <h3 className="font-mono text-xs text-primary-muted uppercase mb-4 tracking-widest">Select Subject</h3>
        <div className="flex flex-col gap-2 overflow-y-auto">
          {characters.map(c => (
            <button 
              key={c.id} 
              onClick={() => setSelectedCharacterId(c.id)}
              className="text-left px-3 py-2 border border-border rounded hover:border-primary transition-colors flex justify-between items-center"
            >
              <span className="font-serif text-primary">{c.name}</span>
              {c.alive ? (
                <span className="w-2 h-2 rounded-full bg-canon"></span>
              ) : (
                <span className="w-2 h-2 rounded-full bg-danger"></span>
              )}
            </button>
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col border-b border-border overflow-hidden min-h-[300px]">
      
      {/* Header */}
      <div className="flex-none p-3 border-b border-border bg-background flex justify-between items-center">
        <div className="flex items-center gap-3">
          <button 
            onClick={() => setSelectedCharacterId(null)}
            className="text-primary-muted hover:text-primary transition-colors text-xs font-mono"
          >
            ← BACK
          </button>
          <span className="font-serif text-primary font-medium">{character?.name}</span>
        </div>
        <div className="text-[10px] font-mono text-canon border border-canon/30 bg-canon/5 px-2 py-1 rounded">
          {knowledgeCount} FACTS IN MEMORY
        </div>
      </div>

      {/* Chat Log */}
      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 flex flex-col gap-4">
        {chatLog.length === 0 && (
          <div className="text-center text-primary-muted font-mono text-xs mt-10 opacity-50">
            Commence interrogation.<br/>
            Knowledge horizon constrained to Sequence {currentSequence}.
          </div>
        )}
        
        {chatLog.map((msg, i) => (
          <div key={i} className={`flex flex-col ${msg.role === 'user' ? 'items-end' : 'items-start'}`}>
            <span className="text-[10px] font-mono text-primary-muted mb-1 ml-1">
              {msg.role === 'user' ? 'YOU' : character?.name.toUpperCase()}
            </span>
            <div className={`px-3 py-2 rounded-lg text-sm max-w-[90%] font-serif leading-relaxed ${
              msg.role === 'user' 
                ? 'bg-border text-primary' 
                : 'bg-background border border-border text-primary shadow-sm'
            }`}>
              {msg.content}
            </div>
          </div>
        ))}
        {loading && (
          <div className="flex items-center gap-2 text-primary-muted font-mono text-xs">
            <Loader2 className="animate-spin" size={12} /> Synthesizing response...
          </div>
        )}
      </div>

      {/* Input */}
      <form onSubmit={handleChat} className="flex-none p-3 border-t border-border bg-background flex gap-2">
        <input 
          type="text" 
          value={input}
          onChange={e => setInput(e.target.value)}
          placeholder={`Ask ${character?.name.split(' ')[0]}...`}
          className="flex-1 bg-transparent border border-border rounded px-3 py-2 text-sm font-serif focus:outline-none focus:border-primary transition-colors"
        />
        <button 
          type="submit"
          disabled={!input.trim() || loading}
          className="bg-primary text-background p-2 rounded disabled:opacity-50 hover:bg-white transition-colors"
        >
          <Send size={16} />
        </button>
      </form>

    </div>
  );
}
