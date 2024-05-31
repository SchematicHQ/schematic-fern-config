# Schematic Fern Configuration

This repository contains your Fern Configuration:

- [OpenAPI spec](./openapi/openapi.yml)
- [Generators config](./fern/generators.yml)

## Validating your API Definition

To validate your API, run:

```sh
npm install -g fern-api # only required once
fern check
```

## Generating your SDK

To upgrade your SDK, click on `Actions` and then hit `Release Python SDK`. Under the 
hood, our CLI powers this action: 

```sh
npm install -g fern-api # only required once
fern generate --docs --preview
```
