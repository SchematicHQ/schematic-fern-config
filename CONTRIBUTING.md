# Contributing

This repo holds the Fern configuration and MDX source for [docs.schematichq.com](https://docs.schematichq.com).

## Docs page conventions

Read this before adding a page, adding a hub, or changing navigation.

### The rules, in short

| Question | Rule |
|---|---|
| Cards or bullets on a hub page? | 6 links or fewer, use `CardGroup`. 7 or more, use markdown bullets. |
| How many overview pages per group? | Exactly one, named `overview.mdx`, living in the group's directory. |
| How many cross-cutting hub pages? | Four. Landing, `/use-cases`, `/developers`, `/product-teams`. Adding a fifth needs a reason written into this file. |
| Hub page or a `docs.yml` `link:` entry? | Sidebar cross-listing uses `link:`. Prose cross-listing uses a hub. A given cross-reference lives in exactly one of the two, never both. |
| `slug:` frontmatter? | Required on every new page. Absolute, no leading slash. |
| `description:` frontmatter? | Required on every new page. One sentence, states the outcome. |
| Can I edit `developer_resources/sdks/*`? | Six of the fifteen are generated. Check the list below before touching any of them. |
| How do I check my work? | `fern check` locally, then the preview URL the PR bot posts. |

---

### 1. Hub pages: cards or bullets

A hub page is a page whose job is routing the reader onward rather than teaching something. Overview pages and the landing page are hubs.

| Link count | Style | Why |
|---|---|---|
| 6 or fewer | `CardGroup` with `cols={2}` or `cols={3}` | Cards are large and carry an icon, so a short list reads as a set of real choices. |
| 7 or more | Markdown bullets, grouped under `##` headings | A card grid past two rows stops being scannable and turns into a wall of equal-weight tiles. |

One page may use both. Put the primary fork in cards at the top, then everything else in bullets below. That is the shape the rebuilt landing page should take: two cards for the real fork, bullets for the rest.

Do not size the grid to fill the row. If a section has 4 links, `cols={2}` over two rows beats `cols={3}` with a ragged tail.

**Cards, worked example.** `fern/docs/pages/developer_resources/sdks/overview.mdx` is over the threshold at 15 SDK cards and should be bullets by this rule, so use the smaller groups in `fern/docs/pages/get_started/overview.mdx` as the pattern instead:

```mdx
<CardGroup cols={3}>
  <Card title="Quickstart App" icon="fa-solid fa-circle-play" href="/quickstart/overview">
    Try out Schematic's core features with our quickstart app.
  </Card>
  ...
</CardGroup>
```

Icons are Font Awesome class strings (`fa-solid`, `fa-regular`, `fa-brands`). Every card in a group needs one, or the group looks broken.

**Bullets, worked example.** `fern/docs/pages/use-cases/overview.mdx` carries 23 links across five `##` sections. Each entry is a bolded link plus a one-line description of the outcome:

```mdx
## AI monetization

Selling AI means protecting two things: your margins, and your customers' trust.

- **[Show customers what an action will cost](/use-cases/pre-flight)** — pre-flight cost previews so customers know the price before they run an expensive action.
- **[Protect your margins](/use-cases/margin-protection)** — enforce the limits you priced for in real time, before heavy usage erodes a plan.
```

Match that pattern when adding to a bulleted hub: bolded link, a spaced em dash (U+2014), then a lowercase sentence describing the outcome, ending in a full stop. One line per entry, no nesting. The em dash separator is a hub-bullet convention only, not house style for body prose.

The same page may appear under more than one heading on a bulleted hub. Cross-listing is the point of a hub, and `pre-flight` already appears under two headings.

---

### 2. Every content group gets exactly one overview page

Ten exist today: `billing`, `catalog`, `components`, `developer_resources/sdks`, `feature-management`, `get_started`, `integrations`, `playbooks`, `quickstart`, `use-cases`.

The overview page is the group's first nav entry and answers, in order:

1. What this group covers, in one or two sentences of plain prose.
2. What you can do with it, as a short list.
3. Where to go next, as links to the pages in the group.

It is not a duplicate of the sidebar. If the overview page is only a list of the pages already visible in the sidebar beneath it, it is doing no work. Say what the group is for, then link.

A group without a real overview page is a defect. `fern/docs/pages/integrations/overview.mdx` is currently frontmatter and nothing else.

---

### 3. The hub ceiling is four

Hub pages are hand-maintained plain links, so they rot silently. Rename a page and the hub keeps pointing at a 404 without any build failure. `use-cases/overview.mdx` alone carries 23 hardcoded paths.

| Hub | Axis it routes on | Status |
|---|---|---|
| Landing page (`get_started/overview.mdx`) | Intent, then role | Being rebuilt, DEV-300 |
| `/use-cases` | Job to be done | Exists |
| `/developers` | Role | Planned, DEV-283 |
| `/product-teams` | Role | Planned, DEV-313 |

Group overview pages (section 2) do not count against this ceiling. They route within one group and are bounded by that group's page list. The ceiling applies to hubs that cross-cut groups, which are the ones that rot.

**Test for a fifth cross-cutting hub.** All four must be true:

1. It routes on an axis none of the existing four already covers. A second role hub or a second job hub is a rewrite of an existing one, not a new one.
2. It cross-lists at least 8 pages that already exist. Fewer than that belongs as a section on an existing hub.
3. Its links are traceable to it. Someone links to it from the sidebar or the landing page, so it is reachable without knowing the URL.
4. A named person owns keeping it current.

If a proposed hub fails any of these, add a `##` section to an existing hub instead.

---

### 4. Hub pages versus `docs.yml` `link:` entries

Two mechanisms cross-list the same page in two places. They are not interchangeable.

| Mechanism | Where it shows up | Use it for |
|---|---|---|
| `link:` entry in `fern/docs.yml` | The sidebar, under a second section | Cross-listing a page into a second sidebar section, or deep-linking an anchor within a long page |
| Bullet or card on a hub page | Page body only | Cross-listing with an explanation of why the reader would want it |

Seventeen `link:` entries exist today, in two shapes:

```yaml
# Cross-list an existing page into a second section
- link: Pre-flight cost previews
  href: /use-cases/pre-flight

# Surface anchors within one long page as sidebar children
- link: Initial Plan
  href: /catalog/configuration#initial-plan
```

**The rule: one cross-reference, one mechanism.** If a page is cross-listed into a sidebar section with `link:`, do not also add it to a hub page under a heading that means the same thing. Pick one and delete the other. The two drift, and the reader who follows one has no way to know the other exists.

Which to pick:

- The reader would find it by scanning the sidebar for a topic, and no explanation is needed. Use `link:`.
- The reader needs a sentence on why this page is relevant to what they are doing. Use a hub bullet.
- It is an anchor inside a page rather than a page. Use `link:`, since a hub cannot expand in the sidebar.

`link:` hrefs are hardcoded strings that Fern does not validate against real pages, so treat them the same as hub links: change a slug, grep for it.

---

### 5. `slug:` frontmatter is required and it wins

Fern reads an absolute `slug:` from frontmatter and it overrides the path the navigation would otherwise derive. 118 of the 125 pages under `fern/docs/pages/` declare one. The seven that do not are six API object pages inside the API Reference tab plus one empty file.

```yaml
---
title: Run credit-based billing
slug: use-cases/credit-billing
description: Sell a prepaid credit balance that burns down as customers use features.
---
```

Consequences a new page author needs to know:

- **The URL does not follow the directory or the sidebar.** `fern/docs/pages/production_readiness/availability.mdx` declares `slug: architecture/availability` and serves at `/architecture/availability`. Do not infer a page's URL from where its file lives, and do not infer it from the sidebar group either.
- **Moving a file changes nothing.** Regrouping the sidebar or moving an MDX file does not change a URL, because the slug is pinned in the file.
- **Changing a slug breaks links silently.** Nothing in the build catches an internal link to a slug that no longer exists. If you change a slug, `grep -rn "old/slug" fern/` across `.mdx` and `docs.yml`, fix every hit, and add a redirect.
- **Redirects live in the `redirects:` block at the bottom of `fern/docs.yml`.** 44 exist. Add to that block, and point the new redirect at the final destination rather than at another redirect, so no chains form.

Format: no leading slash, no trailing slash, lowercase, hyphens between words. Match the group prefix of the pages around it.

---

### 6. `description:` frontmatter is required

Fern feeds `description:` into the auto-generated `llms.txt`, which is how coding agents and search index the docs. A page without a description is close to invisible to retrieval. Only 33 of 125 pages carry one today, so new pages must not add to that gap.

Model to copy, from `fern/docs/pages/use-cases/credit-billing.mdx`:

```yaml
description: Sell a prepaid credit balance that burns down as customers use features.
```

What makes it work:

- One sentence, roughly 10 to 20 words, ending in a full stop.
- Leads with a verb describing what the reader accomplishes.
- Names the concrete thing ("prepaid credit balance", "burns down") rather than the abstraction.
- Does not restate the title, and does not open with "This page describes".

Weak: `description: Learn about credits in Schematic.`
Strong: `description: Sell a prepaid credit balance that burns down as customers use features.`

Write the description before writing the page. If it is hard to write in one sentence, the page is covering more than one topic.

---

### 7. Generated pages: do not hand-edit

Six pages under `fern/docs/pages/developer_resources/sdks/` are rewritten verbatim from the READMEs in their SDK repos by `scripts/sync_sdk_readmes.py`:

`go.mdx`, `java.mdx`, `nodejs.mdx`, `python.mdx`, `ruby.mdx`, `csharp.mdx`

Edit the README in the SDK repo instead. An edit made here is reverted the next time the sync runs, and the weekly `Sync SDK READMEs` workflow will open a draft PR undoing it.

```sh
scripts/sync_sdk_readmes.py          # rewrite the pages
scripts/sync_sdk_readmes.py --check  # report drift, exit 1
```

The other nine pages in that directory (`react`, `react-native`, `vue`, `angular`, `nextjs`, `javascript`, `php`, `cross-platform-features`, `overview`) are hand-maintained and safe to edit. `php.mdx` is deliberately excluded from the sync because its README is OpenAPI generator output.

Anything under `fern/docs/pages/api_documentation/` and the API Reference tab is driven by the OpenAPI spec. Change `openapi-overrides.yml` or `overrides.yaml`, not the generated surface.

---

### 8. Verifying a docs change

```sh
npm install -g fern-api   # only required once
fern check

# or, without installing
npx fern-api check
```

The CLI package is `fern-api`, not `fern`. Plain `npx fern check` resolves the unrelated `fern` package pinned in `package.json` and fails.

Run it from the repo root. It validates `fern/docs.yml` and the API definition, and it is the same check CI runs in `.github/workflows/fern-check.yml`. It catches a nav entry pointing at a file that does not exist. It does not catch a broken internal link or a `link:` href pointing at a dead slug, so check those by hand.

Then open the PR. `.github/workflows/preview-docs.yml` runs `fern generate --docs --preview` and comments a preview URL on the PR. On that preview, confirm:

- Every nav group expands and every page in it loads.
- Card grids are not ragged and every card has an icon.
- Every link you added or changed resolves, including the `link:` hrefs.
- The page serves at the slug you declared, not the one you assumed from the directory.

---

### Checklist for a new page

- [ ] `title:`, `slug:`, and `description:` in frontmatter
- [ ] Slug is absolute, lowercase, hyphenated, no leading slash
- [ ] Description is one sentence stating the outcome
- [ ] Added to `fern/docs.yml` navigation under exactly one section
- [ ] Linked from its group's `overview.mdx`
- [ ] If cross-listed, cross-listed by one mechanism, not two
- [ ] `npx fern check` passes
- [ ] Preview URL checked
