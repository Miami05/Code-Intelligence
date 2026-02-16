import { create } from 'zustand';
import { Repository } from '../types/repository';

interface AppStore {
  // Selected repository
  selectedRepository: Repository | null;
  setSelectedRepository: (repo: Repository | null) => void;

  // Theme
  theme: 'light' | 'dark';
  toggleTheme: () => void;

  // Sidebar
  sidebarOpen: boolean;
  setSidebarOpen: (open: boolean) => void;
}

export const useStore = create<AppStore>((set) => ({
  selectedRepository: null,
  setSelectedRepository: (repo) => set({ selectedRepository: repo }),

  theme: 'light',
  toggleTheme: () => set((state) => ({ theme: state.theme === 'light' ? 'dark' : 'light' })),

  sidebarOpen: true,
  setSidebarOpen: (open) => set({ sidebarOpen: open }),
}));
