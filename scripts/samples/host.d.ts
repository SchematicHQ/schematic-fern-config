// Host-owned placeholders the components docs samples use without defining.
//
// Policy: only a name the reader's own app owns belongs here, such as its
// auth helper, its router, a value it already holds, or a layout piece it
// writes itself. Never add a name a docs page defines in an earlier block
// of the same page. A block that leans on an earlier block repeats the
// definition or carries `{/* samples: nocheck <reason> */}` on the line
// above its fence. A placeholder here hides a sample that forgot its
// import, so keep the list short and the shapes loose.
//
// Each name is a global. A block's own declaration of the same name shadows it.

import type { ComponentType, ReactNode } from "react";
import type { AccessTokenResult } from "@schematichq/schematic-js";
import type { SessionInput } from "@schematichq/schematic-react";

declare global {
  // Pieces of the reader's app.
  const Skeleton: ComponentType<any>;
  const Summary: ComponentType<any>;
  const PeriodToggle: ComponentType<any>;
  const CurrencyPicker: ComponentType<any>;
  const NotFound: ComponentType<any>;
  function getSession(): Promise<{ companyId?: string; userId?: string } | null>;
  function fetchAccessToken(): Promise<AccessTokenResult>;
  function openTopUp(creditId: string): void;
  function openTopUpSettings(): void;
  function showGoodbye(): void;
  const router: { push(url: string): void };

  // Values the reader's app already holds.
  const company: { id: string; name?: string };
  const user: { id: string; email?: string; name?: string };
  const session: SessionInput;
  const publishableKey: string;
  const token: string;
  const children: ReactNode;
  const plan: { id: string; name?: string };
  const paymentMethodId: string;
}

export {};
