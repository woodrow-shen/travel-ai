import { describe, it, expect, beforeEach } from "vitest";
import { useCompareStore } from "../compare";

describe("useCompareStore", () => {
  beforeEach(() => {
    useCompareStore.setState({
      selectedIds: [],
      selectedType: "flight",
    });
  });

  it("starts with empty selection", () => {
    const state = useCompareStore.getState();
    expect(state.selectedIds).toEqual([]);
    expect(state.selectedType).toBe("flight");
  });

  describe("toggleItem", () => {
    it("adds an item", () => {
      useCompareStore.getState().toggleItem("f-1", "flight");
      expect(useCompareStore.getState().selectedIds).toEqual(["f-1"]);
    });

    it("removes an already-selected item", () => {
      useCompareStore.getState().toggleItem("f-1", "flight");
      useCompareStore.getState().toggleItem("f-1", "flight");
      expect(useCompareStore.getState().selectedIds).toEqual([]);
    });

    it("allows up to 4 items", () => {
      const store = useCompareStore.getState();
      store.toggleItem("f-1", "flight");
      useCompareStore.getState().toggleItem("f-2", "flight");
      useCompareStore.getState().toggleItem("f-3", "flight");
      useCompareStore.getState().toggleItem("f-4", "flight");
      expect(useCompareStore.getState().selectedIds).toHaveLength(4);
    });

    it("ignores 5th item (max 4)", () => {
      useCompareStore.getState().toggleItem("f-1", "flight");
      useCompareStore.getState().toggleItem("f-2", "flight");
      useCompareStore.getState().toggleItem("f-3", "flight");
      useCompareStore.getState().toggleItem("f-4", "flight");
      useCompareStore.getState().toggleItem("f-5", "flight");
      expect(useCompareStore.getState().selectedIds).toHaveLength(4);
      expect(useCompareStore.getState().selectedIds).not.toContain("f-5");
    });

    it("resets selection when switching type", () => {
      useCompareStore.getState().toggleItem("f-1", "flight");
      useCompareStore.getState().toggleItem("f-2", "flight");

      // Switch to hotel
      useCompareStore.getState().toggleItem("h-1", "hotel");
      const state = useCompareStore.getState();
      expect(state.selectedIds).toEqual(["h-1"]);
      expect(state.selectedType).toBe("hotel");
    });
  });

  describe("clearSelection", () => {
    it("clears all selected ids", () => {
      useCompareStore.getState().toggleItem("f-1", "flight");
      useCompareStore.getState().toggleItem("f-2", "flight");

      useCompareStore.getState().clearSelection();
      expect(useCompareStore.getState().selectedIds).toEqual([]);
    });
  });

  describe("setType", () => {
    it("changes type and clears selection", () => {
      useCompareStore.getState().toggleItem("f-1", "flight");
      useCompareStore.getState().setType("hotel");

      const state = useCompareStore.getState();
      expect(state.selectedType).toBe("hotel");
      expect(state.selectedIds).toEqual([]);
    });
  });
});
