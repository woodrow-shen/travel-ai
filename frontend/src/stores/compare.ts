import { create } from "zustand";
import type { SearchType } from "@/types";

const MAX_COMPARE = 4;

interface CompareState {
  selectedIds: string[];
  selectedType: SearchType;

  toggleItem: (id: string, type: SearchType) => void;
  clearSelection: () => void;
  setType: (type: SearchType) => void;
}

export const useCompareStore = create<CompareState>((set) => ({
  selectedIds: [],
  selectedType: "flight",

  toggleItem: (id, type) =>
    set((state) => {
      if (state.selectedType !== type) {
        return { selectedIds: [id], selectedType: type };
      }
      const exists = state.selectedIds.includes(id);
      if (exists) {
        return { selectedIds: state.selectedIds.filter((i) => i !== id) };
      }
      if (state.selectedIds.length >= MAX_COMPARE) {
        return state;
      }
      return { selectedIds: [...state.selectedIds, id] };
    }),

  clearSelection: () => set({ selectedIds: [] }),

  setType: (type) => set({ selectedType: type, selectedIds: [] }),
}));
