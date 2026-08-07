# Marketing to docs link contract

The canonical list of docs URLs the marketing site is safe to link to. Every URL here is covered by a `redirects:` entry in `fern/docs.yml`, so docs can be restructured without breaking the site.

If you need to link somewhere not on this list, open a docs ticket first so a redirect ships alongside it. That is the whole point of the contract: docs owns its own structure, and marketing gets URLs that do not move.

## Before you link, read this

**Fern serves HTTP 200 for unknown slugs.** A dead docs link returns 200 with a generic page titled `Documentation`. A status-code check will pass on a 404. Verify by title instead:

```sh
curl -sL https://docs.schematichq.com<slug> | grep -oiE "<title>[^<]*</title>"
```

If the title comes back as bare `Documentation`, the link is dead.

**Page slugs do not match file paths.** Several pages were re-slugged during the docs IA work, so do not infer a URL from a file path or from an older link you found somewhere. Use this table.

## Canonical URLs

All relative to `https://docs.schematichq.com`.

| What you are linking to | URL |
| --- | --- |
| Docs home | `/overview` |
| What is Schematic | `/what-is-schematic` |
| Concepts and vocabulary | `/concepts` |
| Quickstart | `/quickstart/overview` |
| Developer landing page | `/developers` |
| For product teams | `/product-teams` |
| Use cases index | `/use-cases/overview` |

### Components

| What you are linking to | URL |
| --- | --- |
| Components overview | `/components/overview` |
| Customer portal and checkout | `/components/customer-portal` |
| Pricing table | `/components/pricing-table` |
| Element library | `/components/element-library` |
| Adding components to your app | `/components/set-up` |

### Billing and credits

| What you are linking to | URL |
| --- | --- |
| Billing overview | `/billing/overview` |
| Credit burndown, including auto top-up | `/billing/credit-burndown` |
| Usage-based billing | `/billing/usage-based-billing` |
| Seat-based billing | `/billing/seat-based-billing` |
| Credit billing use case | `/use-cases/credit-billing` |
| Real-time ledger and holds | `/use-cases/credit-ledger` |
| Usage-based pricing use case | `/use-cases/usage-based-pricing` |
| Custom plans | `/catalog/custom-plans` |

### Trust and enterprise

| What you are linking to | URL |
| --- | --- |
| Security, SOC 2, encryption, SSO | `/production_readiness/security` |
| Availability, HA strategies, Replicator | `/production_readiness/availability` |
| Observability and support | `/production_readiness/observability` |
| Roles and permissions | `/production_readiness/roles-and-permissions` |

Note that these live under `/production_readiness/`, not `/architecture/`. The `/architecture/*` URLs still work as redirects, but link to the canonical form above.

### Integrations and AI tooling

| What you are linking to | URL |
| --- | --- |
| Stripe integration | `/integrations/stripe` |
| Integrations index | `/integrations/overview` |
| Webhooks | `/integrations/webhooks` |
| AI tooling for developers, including MCP | `/for-developers` |
| The MCP section specifically | `/for-developers#model-context-protocol-mcp` |

## Short aliases

These shorter URLs all redirect to the canonical pages above and are safe to use in body copy where a shorter link reads better:

`/security` · `/availability` · `/observability` · `/roles-and-permissions` · `/quickstart` · `/components` · `/billing` · `/credits` · `/credit-burndown` · `/customer-portal` · `/pricing-table` · `/webhooks` · `/integrations` · `/sdks` · `/use-cases` · `/playbooks` · `/trials` · `/add-ons` · `/mcp` · `/flags` · `/features`

`/concepts` and `/developers` are canonical page slugs rather than aliases, so they appear in the tables above.

## Known corrections

Four links on the v2 build resolve but land on a page that does not answer the label. These are tracked in DEV-284 and DEV-296 and need fixing on the marketing side.

| Link on /v2 | Currently points at | Should point at |
| --- | --- | --- |
| Enterprise → Availability → Learn more | `schematic.statuspage.io` | `/production_readiness/availability` |
| Enterprise → Observability → Learn more | `/security` | `/production_readiness/observability` |
| View all components → | docs root | `/components/overview` |
| Developers → Read the docs | docs root | `/quickstart/overview` |

Both `/developers` CTAs (the "Schematic for developers →" link and the footer "Developers" link) should point at `/developers` on the docs site, which is the developer landing page that replaced the marketing `/developers` page.

## Docs to marketing

Docs links back out to the marketing site in three places in `fern/docs.yml`. If any of these URLs move during the site transition, update them here:

- `tabs:` — the Blog tab points at `https://schematichq.com/blog`, the Roadmap tab at `https://roadmap.schematichq.com/`
- `navbar-links:` — a support mailto and the app dashboard
- `footer-links:` — GitHub, LinkedIn, and `https://schematichq.com/`
