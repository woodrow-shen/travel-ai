import type { ApiError } from "@/types";

const BASE_URL = "/api";

class ApiClient {
  private getToken(): string | null {
    if (typeof window === "undefined") return null;
    return localStorage.getItem("access_token");
  }

  private headers(extra: Record<string, string> = {}): HeadersInit {
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...extra,
    };

    const token = this.getToken();
    if (token) {
      headers["Authorization"] = `Bearer ${token}`;
    }

    return headers;
  }

  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const body = await response.json().catch(() => ({
        detail: response.statusText,
      }));
      const error: ApiError = {
        detail: body.detail ?? "An unexpected error occurred",
        status_code: response.status,
      };
      throw error;
    }
    return response.json() as Promise<T>;
  }

  async get<T>(path: string, params?: Record<string, string>): Promise<T> {
    const url = new URL(`${BASE_URL}${path}`, window.location.origin);
    if (params) {
      Object.entries(params).forEach(([key, value]) => {
        if (value !== undefined && value !== "") {
          url.searchParams.set(key, value);
        }
      });
    }

    const response = await fetch(url.toString(), {
      method: "GET",
      headers: this.headers(),
    });

    return this.handleResponse<T>(response);
  }

  async post<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: "POST",
      headers: this.headers(),
      body: body ? JSON.stringify(body) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  async put<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: "PUT",
      headers: this.headers(),
      body: body ? JSON.stringify(body) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  async patch<T>(path: string, body?: unknown): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: "PATCH",
      headers: this.headers(),
      body: body ? JSON.stringify(body) : undefined,
    });

    return this.handleResponse<T>(response);
  }

  async delete<T>(path: string): Promise<T> {
    const response = await fetch(`${BASE_URL}${path}`, {
      method: "DELETE",
      headers: this.headers(),
    });

    return this.handleResponse<T>(response);
  }

  /**
   * Create an SSE connection for streaming responses.
   * Returns an AbortController so the caller can cancel the stream.
   */
  streamSSE(
    path: string,
    body: unknown,
    onEvent: (event: { type: string; data: string }) => void,
    onError?: (error: unknown) => void,
    onDone?: () => void
  ): AbortController {
    const controller = new AbortController();

    const run = async () => {
      try {
        const response = await fetch(`${BASE_URL}${path}`, {
          method: "POST",
          headers: this.headers({ Accept: "text/event-stream" }),
          body: JSON.stringify(body),
          signal: controller.signal,
        });

        if (!response.ok) {
          const errBody = await response.json().catch(() => ({
            detail: response.statusText,
          }));
          throw {
            detail: errBody.detail ?? "Stream request failed",
            status_code: response.status,
          } as ApiError;
        }

        const reader = response.body?.getReader();
        if (!reader) throw new Error("No response body");

        const decoder = new TextDecoder();
        let buffer = "";

        while (true) {
          const { done, value } = await reader.read();
          if (done) break;

          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split("\n");
          buffer = lines.pop() ?? "";

          let currentEventType = "text";

          for (const line of lines) {
            if (line.startsWith("event: ")) {
              currentEventType = line.slice(7).trim();
            } else if (line.startsWith("data: ")) {
              const data = line.slice(6);
              onEvent({ type: currentEventType, data });
              currentEventType = "text";
            } else if (line.trim() === "") {
              currentEventType = "text";
            }
          }
        }

        onDone?.();
      } catch (err: unknown) {
        if (err instanceof DOMException && err.name === "AbortError") {
          onDone?.();
          return;
        }
        onError?.(err);
      }
    };

    run();
    return controller;
  }
}

export const api = new ApiClient();
