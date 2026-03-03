"use client";

import { useState, useEffect, useCallback } from "react";
import { api } from "@/lib/api";
import type { UserResponse } from "@/types";

interface AuthState {
  user: UserResponse | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}

export function useAuth() {
  const [state, setState] = useState<AuthState>({
    user: null,
    isAuthenticated: false,
    isLoading: true,
  });

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      setState({ user: null, isAuthenticated: false, isLoading: false });
      return;
    }

    try {
      const user = await api.get<UserResponse>("/auth/me");
      setState({ user, isAuthenticated: true, isLoading: false });
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      setState({ user: null, isAuthenticated: false, isLoading: false });
    }
  }, []);

  useEffect(() => {
    fetchUser();
  }, [fetchUser]);

  const login = useCallback(() => {
    window.location.href = "/api/auth/google";
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setState({ user: null, isAuthenticated: false, isLoading: false });
    window.location.href = "/";
  }, []);

  const setTokens = useCallback(
    (accessToken: string, refreshToken?: string) => {
      localStorage.setItem("access_token", accessToken);
      if (refreshToken) {
        localStorage.setItem("refresh_token", refreshToken);
      }
      fetchUser();
    },
    [fetchUser]
  );

  return {
    ...state,
    login,
    logout,
    setTokens,
    refreshUser: fetchUser,
  };
}
