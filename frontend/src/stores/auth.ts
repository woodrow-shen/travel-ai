import { create } from "zustand";
import type { UserResponse } from "@/types";

interface AuthState {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  _initialized: boolean;

  setUser: (user: UserResponse | null) => void;
  setLoading: (loading: boolean) => void;
  markInitialized: () => void;
  reset: () => void;
}

const initialState = {
  user: null,
  isAuthenticated: false,
  isLoading: true,
  _initialized: false,
};

export const useAuthStore = create<AuthState>((set) => ({
  ...initialState,

  setUser: (user) => set({ user, isAuthenticated: user !== null }),

  setLoading: (isLoading) => set({ isLoading }),

  markInitialized: () => set({ _initialized: true }),

  reset: () =>
    set({ user: null, isAuthenticated: false, isLoading: false, _initialized: true }),
}));
