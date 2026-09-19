"use client";

import { useState } from "react";
import { api, BranchDiffResponse } from "@/lib/api";
import { useAppContext } from "./AppProvider";
import { GitBranch, Loader2 } from "lucide-react";
import BranchDiff from "./BranchDiff";

export default function BranchLab() {
  const { storyId, branchId, setBranchId, currentSequence } = useAppContext();
  
  const [change, setChange] = useState("");
  const [loading, setLoading] = useState(false);
  const [diffData, setDiffData] = useState<BranchDiffResponse | null>(null);
  
  // If we are currently ON a branch, show the diff
  const handleSimulate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!storyId || !change.trim()) return;

    try {
      setLoading(true);
      // Create branch
      const res = await api.createBranch(storyId, currentSequence, change, branchId);
      
      // Fetch diff
      const diff = await api.getBranchDiff(res.branch.id);
      
      setBranchId(res.branch.id);
      setDiffData(diff);
      setChange("");
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleReturn = () => {
    setBranchId("canon");
    setDiffData(null);
  };

  if (branchId !== "canon" && diffData) {
    return (
      <div className="flex-1 flex flex-col min-h-[300px]">
        <div className="flex-none p-3 border-b border-border bg-generated/10 flex justify-between items-center">
          <div className="flex items-center gap-2 text-generated font-mono text-sm uppercase">
            <GitBranch size={16} /> WHAT-IF ACTIVE
          </div>
          <button 
            onClick={handleReturn}
            className="text-xs font-mono border border-generated/30 text-generated px-2 py-1 rounded hover:bg-generated/20 transition-colors"
          >
            RETURN TO CANON
          </button>
        </div>
        <div className="flex-1 overflow-y-auto">
          <BranchDiff diff={diffData} />
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col min-h-[250px] p-6 bg-panel">
      <div className="flex items-center gap-2 text-primary font-serif text-lg mb-4">
        <GitBranch size={20} className="text-generated" /> Create Alternate Timeline
      </div>
      
      <p className="text-primary-muted text-sm font-serif mb-6 leading-relaxed">
        Propose a change at Sequence {currentSequence}. The narrative engine will branch the timeline, enforce consistency, and simulate downstream consequences without altering canon.
      </p>

      <form onSubmit={handleSimulate} className="flex flex-col gap-4">
        <div className="relative">
          <textarea
            value={change}
            onChange={e => setChange(e.target.value)}
            placeholder="What if..."
            className="w-full bg-background border border-border rounded-lg p-3 text-sm font-serif min-h-[100px] focus:outline-none focus:border-generated transition-colors resize-none"
          />
          <div className="absolute bottom-3 right-3 text-xs font-mono text-primary-muted">
            SEQ {currentSequence}
          </div>
        </div>
        
        <button 
          type="submit"
          disabled={!change.trim() || loading}
          className="bg-generated text-white font-mono uppercase text-sm py-2 px-4 rounded hover:bg-generated/90 disabled:opacity-50 flex items-center justify-center gap-2 transition-colors"
        >
          {loading ? (
            <><Loader2 size={16} className="animate-spin" /> Simulating Branch...</>
          ) : (
            "Diverge Timeline"
          )}
        </button>
      </form>
    </div>
  );
}
