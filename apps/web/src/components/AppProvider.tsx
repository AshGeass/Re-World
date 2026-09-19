"use client";

import React, { createContext, useContext, useState, ReactNode } from 'react';
import { WorldStateSummary } from '@/lib/api';

interface AppState {
  storyId: string | null;
  branchId: string;
  currentSequence: number;
  worldSummary: WorldStateSummary | null;
  selectedCharacterId: string | null;
  
  setStoryId: (id: string | null) => void;
  setBranchId: (id: string) => void;
  setCurrentSequence: (seq: number) => void;
  setWorldSummary: (summary: WorldStateSummary | null) => void;
  setSelectedCharacterId: (id: string | null) => void;
}

const AppContext = createContext<AppState | undefined>(undefined);

export function AppProvider({ children }: { children: ReactNode }) {
  const [storyId, setStoryId] = useState<string | null>(null);
  const [branchId, setBranchId] = useState<string>("canon");
  const [currentSequence, setCurrentSequence] = useState<number>(0);
  const [worldSummary, setWorldSummary] = useState<WorldStateSummary | null>(null);
  const [selectedCharacterId, setSelectedCharacterId] = useState<string | null>(null);

  return (
    <AppContext.Provider value={{
      storyId, setStoryId,
      branchId, setBranchId,
      currentSequence, setCurrentSequence,
      worldSummary, setWorldSummary,
      selectedCharacterId, setSelectedCharacterId
    }}>
      {children}
    </AppContext.Provider>
  );
}

export function useAppContext() {
  const context = useContext(AppContext);
  if (context === undefined) {
    throw new Error('useAppContext must be used within an AppProvider');
  }
  return context;
}
