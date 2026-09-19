export const API_BASE = 'http://localhost:8000/api';

export interface Story {
  id: string;
  title: string;
  description: string;
}

export interface WorldStateSummary {
  story_id: string;
  branch_id: string;
  current_sequence: number;
  current_label: string;
  character_count: number;
  event_count: number;
  relationship_count: number;
  knowledge_count: number;
}

export interface TimelineEvent {
  id: string;
  title: string;
  description: string;
  sequence: number;
  event_type: string;
  participants: string[];
  canonical: boolean;
  branch_id: string | null;
}

export interface Character {
  id: string;
  name: string;
  description: string;
  personality: string[];
  goals: string[];
  current_location: string | null;
  alive: boolean;
  aliases: string[];
}

export interface ChatResponse {
  success: boolean;
  output: string;
  character_id: string;
  sequence: number;
  knowledge_count: number;
  errors: string[];
}

export interface BranchInfo {
  id: string;
  story_id: string;
  name: string;
  description: string;
  parent_branch_id: string | null;
  divergence_event_id: string | null;
  divergence_sequence: number;
  canonical: boolean;
}

export interface DiffEntry {
  event_id: string;
  title: string;
  change_type: 'added' | 'removed' | 'changed';
  canon_description?: string;
  branch_description?: string;
  sequence: number;
}

export interface ConsistencyIssue {
  type: string;
  message: string;
  event_ids?: string[];
  character_ids?: string[];
  severity?: string;
}

export interface ConsistencyResponse {
  valid: boolean;
  branch_id: string;
  issues: ConsistencyIssue[];
  summary: string;
}

export interface BranchDiffResponse {
  branch_id: string;
  canon_branch_id: string;
  events_added: DiffEntry[];
  events_removed: DiffEntry[];
  events_changed: DiffEntry[];
  characters_affected: string[];
  relationships_changed: number;
  ripple_depth: number;
  total_changes: number;
}

export const api = {
  async getStories(): Promise<Story[]> {
    const res = await fetch(`${API_BASE}/stories/`);
    if (!res.ok) throw new Error('Failed to fetch stories');
    const data = await res.json();
    return data.stories;
  },

  async uploadStory(file: File, title: string) {
    const formData = new FormData();
    formData.append('file', file);
    formData.append('title', title);
    const res = await fetch(`${API_BASE}/stories/upload`, {
      method: 'POST',
      body: formData,
    });
    if (!res.ok) throw new Error('Upload failed');
    return res.json();
  },

  async getWorldSummary(storyId: string, branchId: string = 'canon'): Promise<WorldStateSummary> {
    const res = await fetch(`${API_BASE}/world-state/${storyId}/${branchId}/summary`);
    if (!res.ok) throw new Error('Failed to fetch world summary');
    return res.json();
  },

  async getTimeline(storyId: string, branchId: string = 'canon', upTo?: number): Promise<{ events: TimelineEvent[], max_sequence: number }> {
    const url = new URL(`${API_BASE}/timelines/${storyId}/${branchId}`);
    if (upTo !== undefined) url.searchParams.append('up_to', upTo.toString());
    const res = await fetch(url.toString());
    if (!res.ok) throw new Error('Failed to fetch timeline');
    return res.json();
  },

  async getCharacters(storyId: string, branchId: string = 'canon'): Promise<Character[]> {
    const res = await fetch(`${API_BASE}/characters/${storyId}?branch_id=${branchId}`);
    if (!res.ok) throw new Error('Failed to fetch characters');
    const data = await res.json();
    return data.characters;
  },

  async getCharacter(storyId: string, characterId: string, branchId: string = 'canon'): Promise<Character> {
    const res = await fetch(`${API_BASE}/characters/${storyId}/${characterId}?branch_id=${branchId}`);
    if (!res.ok) throw new Error('Failed to fetch character');
    return res.json();
  },

  async getCharacterKnowledge(storyId: string, characterId: string, sequence: number, branchId: string = 'canon'): Promise<{facts: unknown[], total: number}> {
    const res = await fetch(`${API_BASE}/characters/${storyId}/${characterId}/knowledge?sequence=${sequence}&branch_id=${branchId}`);
    if (!res.ok) throw new Error('Failed to fetch character knowledge');
    return res.json();
  },

  async chatWithCharacter(storyId: string, characterId: string, sequence: number, message: string, branchId: string = 'canon'): Promise<ChatResponse> {
    const res = await fetch(`${API_BASE}/chat/`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        story_id: storyId,
        character_id: characterId,
        sequence,
        message,
        branch_id: branchId,
      }),
    });
    if (!res.ok) throw new Error('Chat failed');
    return res.json();
  },

  async createBranch(storyId: string, sequence: number, change: string, parentBranchId: string = 'canon') {
    const res = await fetch(`${API_BASE}/branches/create`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        story_id: storyId,
        parent_branch_id: parentBranchId,
        sequence,
        change,
      }),
    });
    if (!res.ok) throw new Error('Failed to create branch');
    return res.json();
  },

  async getBranchDiff(branchId: string): Promise<BranchDiffResponse> {
    const res = await fetch(`${API_BASE}/branches/${branchId}/diff`);
    if (!res.ok) throw new Error('Failed to fetch branch diff');
    return res.json();
  },

  async checkConsistency(branchId: string): Promise<ConsistencyResponse> {
    const res = await fetch(`${API_BASE}/branches/${branchId}/validate`, { method: 'POST' });
    if (!res.ok) throw new Error('Failed to check consistency');
    return res.json();
  }
};
