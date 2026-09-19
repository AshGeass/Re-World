"use client";

import { useAppContext } from "./AppProvider";
import TimelineViz from "./TimelineViz";
import CharacterPanel from "./CharacterPanel";
import BranchLab from "./BranchLab";

export default function WorldDashboard() {
  const { worldSummary, setStoryId, setBranchId, setSelectedCharacterId } = useAppContext();

  if (!worldSummary) return null;

  return (
    <div className="flex-1 flex flex-col h-full overflow-hidden relative">
      {/* Top Bar for World Info */}
      <div className="flex-none px-6 py-3 border-b border-border bg-panel flex items-center justify-between">
        <div>
          <h2 className="font-serif text-lg text-primary">
            {worldSummary.story_id.replace("_", " ").replace("-", " ").toUpperCase()}
          </h2>
          <div className="text-xs font-mono text-primary-muted flex gap-4 mt-1">
            <span>Branch: <span className={worldSummary.branch_id === 'canon' ? 'text-canon' : 'text-generated'}>{worldSummary.branch_id.toUpperCase()}</span></span>
            <span>Seq: {worldSummary.current_sequence}</span>
            <span>Entities: {worldSummary.character_count}</span>
          </div>
        </div>
        <button 
          onClick={() => {
            setStoryId(null);
            setBranchId("canon");
            setSelectedCharacterId(null);
          }}
          className="text-xs font-mono border border-border px-3 py-1 rounded hover:bg-border transition-colors"
        >
          CLOSE WORLD
        </button>
      </div>

      {/* Main Grid */}
      <div className="flex-1 grid grid-cols-1 lg:grid-cols-12 overflow-hidden">
        
        {/* Left Column: Timeline */}
        <div className="lg:col-span-8 flex flex-col border-r border-border">
          <TimelineViz />
        </div>
        
        {/* Right Column: Character Chat & What If Lab */}
        <div className="lg:col-span-4 flex flex-col overflow-hidden bg-panel/50">
          <CharacterPanel />
          <BranchLab />
        </div>

      </div>
    </div>
  );
}
