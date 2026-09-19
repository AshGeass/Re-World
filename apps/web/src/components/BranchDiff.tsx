"use client";

import { useEffect, useState } from "react";
import { api, BranchDiffResponse, ConsistencyResponse } from "@/lib/api";
import { Plus, Minus, Edit3, Activity } from "lucide-react";

export default function BranchDiff({ diff }: { diff: BranchDiffResponse }) {
  const [consistency, setConsistency] = useState<ConsistencyResponse | null>(null);

  useEffect(() => {
    // Run consistency check on mount
    api.checkConsistency(diff.branch_id).then(setConsistency).catch(console.error);
  }, [diff.branch_id]);

  return (
    <div className="p-4 flex flex-col gap-6">
      
      {/* Ripple Metrics */}
      <div className="grid grid-cols-3 gap-3">
        <div className="bg-background border border-border rounded p-3 text-center">
          <div className="text-2xl font-mono text-generated">{diff.ripple_depth}</div>
          <div className="text-[10px] font-mono text-primary-muted uppercase mt-1">Ripple Depth</div>
        </div>
        <div className="bg-background border border-border rounded p-3 text-center">
          <div className="text-2xl font-mono text-primary">{diff.characters_affected.length}</div>
          <div className="text-[10px] font-mono text-primary-muted uppercase mt-1">Entities Affected</div>
        </div>
        <div className="bg-background border border-border rounded p-3 text-center">
          <div className="text-2xl font-mono text-primary">{diff.relationships_changed}</div>
          <div className="text-[10px] font-mono text-primary-muted uppercase mt-1">Relationships</div>
        </div>
      </div>

      {/* Consistency Status */}
      {consistency && (
        <div className={`border rounded p-3 flex items-start gap-3 ${
          consistency.valid 
            ? 'border-fandom/30 bg-fandom/5 text-fandom' 
            : 'border-danger/30 bg-danger/5 text-danger'
        }`}>
          <Activity size={18} className="mt-0.5 shrink-0" />
          <div>
            <div className="font-mono text-xs font-bold uppercase tracking-wider mb-1">
              Consistency: {consistency.valid ? 'Verified' : 'Contradictions Detected'}
            </div>
            <div className="text-sm font-serif">{consistency.summary}</div>
            
            {!consistency.valid && consistency.issues.length > 0 && (
              <ul className="mt-2 text-xs font-mono space-y-1">
                {consistency.issues.map((issue, i) => (
                  <li key={i} className="flex gap-2">
                    <span className="opacity-50">[{issue.type}]</span>
                    {issue.message}
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}

      {/* Changes List */}
      <div>
        <h3 className="font-mono text-xs uppercase tracking-widest text-primary-muted mb-4 border-b border-border pb-2">
          Structural Divergence ({diff.total_changes})
        </h3>
        
        <div className="space-y-4">
          
          {/* Added */}
          {diff.events_added.map(e => (
            <div key={e.event_id} className="border-l-2 border-generated pl-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="bg-generated/20 text-generated p-0.5 rounded"><Plus size={12} /></span>
                <span className="font-mono text-xs text-generated uppercase">Seq {e.sequence} | Generated</span>
              </div>
              <div className="text-sm font-serif text-primary">{e.title}</div>
              <div className="text-xs text-primary-muted mt-1">{e.branch_description}</div>
            </div>
          ))}

          {/* Changed */}
          {diff.events_changed.map(e => (
            <div key={e.event_id} className="border-l-2 border-canon pl-3">
              <div className="flex items-center gap-2 mb-1">
                <span className="bg-canon/20 text-canon p-0.5 rounded"><Edit3 size={12} /></span>
                <span className="font-mono text-xs text-canon uppercase">Seq {e.sequence} | Altered Canon</span>
              </div>
              <div className="text-sm font-serif text-primary">{e.title}</div>
              <div className="grid grid-cols-2 gap-2 mt-2">
                <div className="bg-background/50 p-2 rounded text-xs line-through opacity-50">
                  {e.canon_description}
                </div>
                <div className="bg-canon/10 p-2 rounded text-xs text-canon">
                  {e.branch_description}
                </div>
              </div>
            </div>
          ))}
          
          {/* Removed */}
          {diff.events_removed.map(e => (
            <div key={e.event_id} className="border-l-2 border-danger pl-3 opacity-60">
              <div className="flex items-center gap-2 mb-1">
                <span className="bg-danger/20 text-danger p-0.5 rounded"><Minus size={12} /></span>
                <span className="font-mono text-xs text-danger uppercase">Seq {e.sequence} | Severed</span>
              </div>
              <div className="text-sm font-serif line-through">{e.title}</div>
            </div>
          ))}

          {diff.total_changes === 0 && (
            <div className="text-center text-primary-muted text-sm font-mono opacity-50 py-4">
              No structural differences detected.
            </div>
          )}

        </div>
      </div>
    </div>
  );
}
