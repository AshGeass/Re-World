"use client";

import { AppProvider } from "./AppProvider";

export function Providers({ children }: { children: React.ReactNode }) {
  return <AppProvider>{children}</AppProvider>;
}
