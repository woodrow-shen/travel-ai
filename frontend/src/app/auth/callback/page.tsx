"use client";

import { useEffect, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { Suspense } from "react";

function AuthCallbackContent() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const [status, setStatus] = useState<"loading" | "success" | "error">(
    "loading"
  );
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    const accessToken = searchParams.get("access_token");
    const refreshToken = searchParams.get("refresh_token");
    const error = searchParams.get("error");

    if (error) {
      setStatus("error");
      setErrorMessage(error);
      return;
    }

    if (!accessToken) {
      // Try to extract from hash fragment (some OAuth flows use fragments)
      const hash = window.location.hash.substring(1);
      const hashParams = new URLSearchParams(hash);
      const hashAccessToken = hashParams.get("access_token");
      const hashRefreshToken = hashParams.get("refresh_token");

      if (hashAccessToken) {
        localStorage.setItem("access_token", hashAccessToken);
        if (hashRefreshToken) {
          localStorage.setItem("refresh_token", hashRefreshToken);
        }
        setStatus("success");
        // Full page reload so Header re-mounts and picks up the new token
        setTimeout(() => { window.location.href = "/"; }, 1000);
        return;
      }

      setStatus("error");
      setErrorMessage("No authentication token received.");
      return;
    }

    localStorage.setItem("access_token", accessToken);
    if (refreshToken) {
      localStorage.setItem("refresh_token", refreshToken);
    }

    setStatus("success");
    // Full page reload so Header re-mounts and picks up the new token
    setTimeout(() => { window.location.href = "/"; }, 1000);
  }, [searchParams, router]);

  return (
    <div className="flex min-h-[60vh] items-center justify-center px-4">
      <div className="text-center">
        {status === "loading" && (
          <>
            <div
              className="mx-auto mb-4 h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]"
              aria-hidden="true"
            />
            <h1 className="text-xl font-semibold">Signing you in...</h1>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              Please wait while we complete authentication.
            </p>
          </>
        )}

        {status === "success" && (
          <>
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-success)]/10">
              <svg
                className="h-6 w-6 text-[var(--color-success)]"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="m4.5 12.75 6 6 9-13.5"
                />
              </svg>
            </div>
            <h1 className="text-xl font-semibold">Successfully signed in</h1>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              Redirecting you to the home page...
            </p>
          </>
        )}

        {status === "error" && (
          <>
            <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-[var(--color-error)]/10">
              <svg
                className="h-6 w-6 text-[var(--color-error)]"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={2}
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M6 18 18 6M6 6l12 12"
                />
              </svg>
            </div>
            <h1 className="text-xl font-semibold text-[var(--color-error)]">
              Authentication Failed
            </h1>
            <p className="mt-2 text-sm text-[var(--color-muted)]">
              {errorMessage}
            </p>
            <button
              onClick={() => router.push("/")}
              className="mt-4 text-sm font-medium text-[var(--color-primary)] hover:underline"
            >
              Return to home
            </button>
          </>
        )}
      </div>
    </div>
  );
}

export default function AuthCallbackPage() {
  return (
    <Suspense
      fallback={
        <div className="flex min-h-[60vh] items-center justify-center">
          <div
            className="h-10 w-10 animate-spin rounded-full border-4 border-[var(--color-border)] border-t-[var(--color-primary)]"
            aria-label="Loading"
          />
        </div>
      }
    >
      <AuthCallbackContent />
    </Suspense>
  );
}
