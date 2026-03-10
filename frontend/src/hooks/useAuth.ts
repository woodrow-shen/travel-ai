"use client";

import { useCallback, useEffect } from "react";
import { api } from "@/lib/api";
import { useAuthStore } from "@/stores/auth";
import type { UserResponse } from "@/types";

export function useAuth() {
  const user = useAuthStore((s) => s.user);
  const isAuthenticated = useAuthStore((s) => s.isAuthenticated);
  const isLoading = useAuthStore((s) => s.isLoading);
  const _initialized = useAuthStore((s) => s._initialized);
  const setUser = useAuthStore((s) => s.setUser);
  const setLoading = useAuthStore((s) => s.setLoading);
  const markInitialized = useAuthStore((s) => s.markInitialized);
  const reset = useAuthStore((s) => s.reset);

  const fetchUser = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      reset();
      return;
    }

    setLoading(true);
    try {
      const userData = await api.get<UserResponse>("/auth/me");
      setUser(userData);
    } catch {
      localStorage.removeItem("access_token");
      localStorage.removeItem("refresh_token");
      reset();
    } finally {
      setLoading(false);
      markInitialized();
    }
  }, [setLoading, setUser, reset, markInitialized]);

  useEffect(() => {
    if (!_initialized) {
      fetchUser();
    }
  }, [_initialized, fetchUser]);

  const login = useCallback(() => {
    window.location.href = "/api/auth/google";
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    reset();
    window.location.href = "/";
  }, [reset]);

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
    user,
    isAuthenticated,
    isLoading,
    login,
    logout,
    setTokens,
    refreshUser: fetchUser,
  };
}
