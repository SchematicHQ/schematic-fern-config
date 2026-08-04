# Schematic Fern Configuration

This repository contains your Fern Configuration:

- [OpenAPI spec](./schematic.yml)
- [Generators config](./fern/generators.yml)
- [Public documentation](./fern/docs/)

Before adding or editing a docs page, read the docs page conventions in [CONTRIBUTING.md](./CONTRIBUTING.md).

## Validating your API Definition

To validate your API, run:

```sh
npm install -g fern-api # only required once
fern check
```

## SDK documentation pages

The server SDK pages under [fern/docs/pages/developer_resources/sdks/](./fern/docs/pages/developer_resources/sdks/)
are generated from the READMEs in the SDK repos — edit the README there, not the
page here. A weekly `Sync SDK READMEs` action opens a draft PR when they drift.
To sync or check by hand:

```sh
scripts/sync_sdk_readmes.py          # rewrite the pages
scripts/sync_sdk_readmes.py --check  # report drift, exit 1
```

The PHP page is the exception, and is maintained by hand.

## Generating your SDK

To upgrade your SDK, click on `Actions` and then hit `Release Python SDK`. Under the
hood, our CLI powers this action:

```sh
npm install -g fern-api # only required once
fern generate --docs --preview
```
