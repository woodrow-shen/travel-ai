"use client";

import { useState } from "react";
import { useTranslations } from "next-intl";
import { useAuth } from "@/hooks/useAuth";
import { useSubscription } from "@/hooks/useSubscription";
import { Button } from "@/components/ui/Button";
import type { SubscriptionType } from "@/types";

export default function SubscriptionsPage() {
  const { isAuthenticated, isLoading: authLoading } = useAuth();
  const t = useTranslations("settings.subscriptions");
  const tc = useTranslations("common");

  if (authLoading) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-[var(--color-muted)]">{tc("loading")}</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="flex min-h-[60vh] items-center justify-center">
        <p className="text-[var(--color-muted)]">{t("signInRequired")}</p>
      </div>
    );
  }

  return <SubscriptionsContent />;
}

function SubscriptionsContent() {
  const {
    emails,
    subscriptions,
    isLoading,
    error,
    addEmail,
    deleteEmail,
    createSubscription,
    toggleSubscription,
    deleteSubscription,
  } = useSubscription();
  const t = useTranslations("settings.subscriptions");

  return (
    <main className="mx-auto max-w-3xl px-4 py-8">
      <h1 className="mb-8 text-2xl font-bold">{t("title")}</h1>

      {error && (
        <div className="mb-6 rounded-lg border border-[var(--color-error)]/30 bg-[var(--color-error)]/10 px-4 py-3 text-sm text-[var(--color-error)]">
          {error}
        </div>
      )}

      <EmailSection emails={emails} isLoading={isLoading} onAdd={addEmail} onDelete={deleteEmail} />

      <SubscriptionList
        subscriptions={subscriptions}
        emails={emails}
        onToggle={toggleSubscription}
        onDelete={deleteSubscription}
      />

      <NewSubscriptionForm emails={emails} onCreate={createSubscription} />
    </main>
  );
}

function EmailSection({
  emails,
  isLoading,
  onAdd,
  onDelete,
}: {
  emails: ReturnType<typeof useSubscription>["emails"];
  isLoading: boolean;
  onAdd: (email: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}) {
  const [newEmail, setNewEmail] = useState("");
  const [adding, setAdding] = useState(false);
  const t = useTranslations("settings.subscriptions.emails");
  const tc = useTranslations("common");

  const handleAdd = async () => {
    if (!newEmail.trim()) return;
    setAdding(true);
    try {
      await onAdd(newEmail.trim());
      setNewEmail("");
    } catch {
      // error is set in store
    } finally {
      setAdding(false);
    }
  };

  return (
    <section className="mb-8">
      <h2 className="mb-4 text-lg font-semibold">{t("title")}</h2>

      {isLoading ? (
        <p className="text-sm text-[var(--color-muted)]">{t("loading")}</p>
      ) : emails.length === 0 ? (
        <p className="mb-4 text-sm text-[var(--color-muted)]">{t("noEmails")}</p>
      ) : (
        <ul className="mb-4 space-y-2">
          {emails.map((e) => (
            <li key={e.id} className="flex items-center justify-between rounded-lg border border-[var(--color-border)] px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">{e.email}</span>
                {e.is_verified ? (
                  <span className="rounded-full bg-green-100 px-2 py-0.5 text-xs font-medium text-green-700">{t("verified")}</span>
                ) : (
                  <span className="rounded-full bg-yellow-100 px-2 py-0.5 text-xs font-medium text-yellow-700">{t("pending")}</span>
                )}
              </div>
              <Button variant="ghost" size="sm" onClick={() => onDelete(e.id)}>
                {tc("remove")}
              </Button>
            </li>
          ))}
        </ul>
      )}

      <div className="flex gap-2">
        <input
          type="email"
          value={newEmail}
          onChange={(e) => setNewEmail(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleAdd()}
          placeholder={t("placeholder")}
          className="flex-1 rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
        />
        <Button size="sm" onClick={handleAdd} isLoading={adding} disabled={!newEmail.trim()}>
          {tc("add")}
        </Button>
      </div>
    </section>
  );
}

function SubscriptionList({
  subscriptions,
  emails,
  onToggle,
  onDelete,
}: {
  subscriptions: ReturnType<typeof useSubscription>["subscriptions"];
  emails: ReturnType<typeof useSubscription>["emails"];
  onToggle: (id: string, isActive: boolean) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
}) {
  const emailMap = new Map(emails.map((e) => [e.id, e.email]));
  const t = useTranslations("settings.subscriptions");
  const tc = useTranslations("common");

  const typeLabel = (type: SubscriptionType) => t(`types.${type}`);

  const configSummary = (config: Record<string, unknown>) => {
    const origin = config.origin as string | undefined;
    const destination = config.destination as string | undefined;
    if (origin && destination) return `${origin} → ${destination}`;
    if (origin) return t("list.from", { origin });
    if (destination) return t("list.to", { destination });
    return "";
  };

  return (
    <section className="mb-8">
      <h2 className="mb-4 text-lg font-semibold">{t("list.title")}</h2>

      {subscriptions.length === 0 ? (
        <p className="text-sm text-[var(--color-muted)]">{t("list.noSubscriptions")}</p>
      ) : (
        <ul className="space-y-2">
          {subscriptions.map((sub) => (
            <li key={sub.id} className="flex items-center justify-between rounded-lg border border-[var(--color-border)] px-4 py-3">
              <div className="flex items-center gap-3">
                <span className="text-sm font-semibold">{typeLabel(sub.type)}</span>
                {configSummary(sub.config) && (
                  <span className="text-sm text-[var(--color-muted)]">{configSummary(sub.config)}</span>
                )}
                <span className="text-xs text-[var(--color-muted)]">
                  → {emailMap.get(sub.email_id) ?? "Unknown"}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => onToggle(sub.id, !sub.is_active)}
                  className={`relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors ${
                    sub.is_active ? "bg-[var(--color-primary)]" : "bg-[var(--color-border)]"
                  }`}
                  role="switch"
                  aria-checked={sub.is_active}
                  aria-label={`Toggle ${typeLabel(sub.type)} subscription`}
                >
                  <span className={`pointer-events-none inline-block h-5 w-5 rounded-full bg-white shadow transition-transform ${sub.is_active ? "translate-x-5" : "translate-x-0"}`} />
                </button>
                <Button variant="ghost" size="sm" onClick={() => onDelete(sub.id)}>
                  {tc("delete")}
                </Button>
              </div>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function NewSubscriptionForm({
  emails,
  onCreate,
}: {
  emails: ReturnType<typeof useSubscription>["emails"];
  onCreate: (emailId: string, type: SubscriptionType, config: Record<string, unknown>) => Promise<void>;
}) {
  const verifiedEmails = emails.filter((e) => e.is_verified);
  const [type, setType] = useState<SubscriptionType>("bug_fare");
  const [emailId, setEmailId] = useState("");
  const [origin, setOrigin] = useState("");
  const [destination, setDestination] = useState("");
  const [creating, setCreating] = useState(false);
  const t = useTranslations("settings.subscriptions");

  const handleCreate = async () => {
    if (!emailId) return;
    setCreating(true);
    try {
      const config: Record<string, unknown> = {};
      if (origin.trim()) config.origin = origin.trim().toUpperCase();
      if (destination.trim()) config.destination = destination.trim().toUpperCase();
      await onCreate(emailId, type, config);
      setOrigin("");
      setDestination("");
    } catch {
      // error is set in store
    } finally {
      setCreating(false);
    }
  };

  return (
    <section>
      <h2 className="mb-4 text-lg font-semibold">{t("new.title")}</h2>

      {verifiedEmails.length === 0 ? (
        <p className="text-sm text-[var(--color-muted)]">{t("new.verifyFirst")}</p>
      ) : (
        <div className="space-y-4 rounded-lg border border-[var(--color-border)] p-4">
          <div>
            <label className="mb-1 block text-sm font-medium">{t("new.type")}</label>
            <select
              value={type}
              onChange={(e) => setType(e.target.value as SubscriptionType)}
              className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              {(["bug_fare", "price_drop", "deal_digest"] as SubscriptionType[]).map((v) => (
                <option key={v} value={v}>{t(`types.${v}`)}</option>
              ))}
            </select>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="mb-1 block text-sm font-medium">{t("new.originIATA")}</label>
              <input
                type="text"
                value={origin}
                onChange={(e) => setOrigin(e.target.value)}
                placeholder="e.g. TPE"
                maxLength={3}
                className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm uppercase outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
            <div>
              <label className="mb-1 block text-sm font-medium">{t("new.destinationIATA")}</label>
              <input
                type="text"
                value={destination}
                onChange={(e) => setDestination(e.target.value)}
                placeholder="e.g. NRT"
                maxLength={3}
                className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm uppercase outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
              />
            </div>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium">{t("new.sendTo")}</label>
            <select
              value={emailId}
              onChange={(e) => setEmailId(e.target.value)}
              className="w-full rounded-lg border border-[var(--color-border)] bg-transparent px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
            >
              <option value="">{t("new.selectEmail")}</option>
              {verifiedEmails.map((e) => (
                <option key={e.id} value={e.id}>{e.email}</option>
              ))}
            </select>
          </div>

          <Button onClick={handleCreate} isLoading={creating} disabled={!emailId}>
            {t("new.create")}
          </Button>
        </div>
      )}
    </section>
  );
}
