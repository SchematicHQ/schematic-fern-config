# Docs conventions

Internal notes for anyone, human or agent, editing the MDX and Fern config in this repo.
Read this before adding a page, adding a hub, or changing navigation.

## Gotchas that have actually bitten people

**`npx fern check` does not work here.** `package.json` pins an unrelated package named `fern`,
so it fails with "could not determine executable to run". Use `npx fern-api check`, or install
`fern-api` globally and run `fern check`. Same check CI runs in `.github/workflows/fern-check.yml`.

**A page's URL follows neither its directory nor its sidebar group.** Fern reads an absolute
`slug:` from frontmatter and it overrides the nav-derived path. Nearly every page declares one.
`get_started/introduction.mdx` declares `slug: what-is-schematic` and serves at
`/what-is-schematic`. Never infer a page's URL from where its file lives.

Consequences: moving a file or regrouping the sidebar changes no URLs. Changing a `slug:` breaks
links silently, because nothing in the build catches an internal link to a slug that no longer
exists. If you change one, `grep -rn "old/slug" fern/` across `.mdx` and `docs.yml`, fix every
hit, and add a redirect pointing at the final destination so no chain forms.

**Six SDK pages are generated and will be overwritten.** `scripts/sync_sdk_readmes.py` rewrites
`go.mdx`, `java.mdx`, `nodejs.mdx`, `python.mdx`, `ruby.mdx`, and `csharp.mdx` from their SDK
repo READMEs. Edit the README in the SDK repo instead. The other nine pages in that directory,
including `react`, `vue`, `nextjs`, and `php`, are hand-maintained and safe to edit.

Anything under `fern/docs/pages/api_documentation/` and the API Reference tab comes from the
OpenAPI spec. Change `openapi-overrides.yml` or `overrides.yaml`, not the generated surface.

## Frontmatter

`title:`, `slug:`, and `description:` are required on every new page.

`slug:` is absolute, lowercase, hyphenated, no leading or trailing slash.

`description:` feeds the auto-generated `llms.txt`, which is how coding agents and search index
these docs. A page without one is close to invisible to retrieval. One sentence, roughly 10 to
20 words, leading with a verb describing what the reader accomplishes, naming the concrete
mechanism. Do not restate the title or open with "Learn about" or "This page".

Weak: `Learn about credits in Schematic.`
Strong: `Sell a prepaid credit balance that burns down as customers use features.`

## Hub pages: cards or bullets

A hub page routes the reader onward rather than teaching something. Overview pages and the docs
home are hubs.

Six links or fewer, use a `CardGroup`. Seven or more, use markdown bullets grouped under `##`
headings. A card grid past two rows stops being scannable. One page may use both, with the
primary fork in cards on top and everything else in bullets below, which is the shape the docs
home takes.

Bulleted hub entries follow `fern/docs/pages/use-cases/overview.mdx`: a bolded link, a spaced em
dash, then a lowercase sentence describing the outcome. That em dash is a hub-bullet convention
only, not house style for body prose.

Every content group gets exactly one overview page, and it should say what the group is for
before it links. An overview that only lists the pages already visible in the sidebar beneath it
is doing no work.

## Product vocabulary

| Concept | Write | Do not write |
|---|---|---|
| Credits | credit balance, credit grant, credit bundle, credit burndown, credit ledger | "wallet", or any other coinage |
| What Schematic is | a usage-based billing engine for AI and software companies | "the entitlement layer", "it sits between your app and your billing system" |
| Where billing happens | Schematic bills, and syncs two ways with Stripe | "Stripe is your source of truth" |
| Entitlements | how enforcement happens | what the product is |

Usage-based billing leads, because it is what brings most readers here. Seat-based and hybrid are
fully supported and must never read as legacy.

Naming Stripe at the feature level is accurate and expected. "Checkout requires a connected
Stripe account" is a feature note and is fine. "Schematic is built on Stripe" is an identity
claim and is wrong.

## Prose style

No em dashes in body prose. Use commas or periods, or restructure. The hub-bullet format above
is the one exception.

No short declarative sentences that just restate the sentence before them.

**Do not add inline comments.** The bar is very high: only when code looks wildly wrong and a
reader needs a paper trail. Never reference a ticket ID or PR number in a comment, and never
write one that restates what the adjacent lines already say. Reasoning belongs in the commit
message and PR description.

## Verifying a change

```sh
npx fern-api check
```

Run from the repo root. It validates `docs.yml` and the API definition, and it catches a nav
entry pointing at a file that does not exist. It does **not** catch a broken internal link or a
`link:` href pointing at a dead slug, so check those by hand.

Then open the PR. `.github/workflows/preview-docs.yml` comments a preview URL. On it, confirm
every nav group expands, every link you touched resolves, and the page serves at the slug you
declared rather than the one you assumed from the directory.
