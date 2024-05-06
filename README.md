[Fern](https://buildwithfern.com) is tool for generating SDKs based on a yaml spec.

The goal is to build out a spec for the Sayari API and then generate:
- Postman collections (not check in to repo, run `make generate` locally and it will show up in /generated/postman)
- Open API spec (not check in to repo, run `make generate` locally and it will show up in /generated/openapi)
  - This happens automatically in our CI and the resultant openapi spec is uploaded to readme.com
- Python SDK [here](https://github.com/sayari-analytics/sayari-python)
- Golang SDK [here](https://github.com/sayari-analytics/sayari-go)
- Node SDK [here](https://github.com/sayari-analytics/sayari-node)
- Java SDK [here](https://github.com/sayari-analytics/sayari-java)

### Docs
Docs are visible [here](https://sayari-analytics.docs.buildwithfern.com)

### CI
The CI in this repo does the following:
Generate & Test: ci.yaml (The CI jobs will run automatically on PR pushes.)
- Generate and Test SDKs
  - Make sure the fern spec is valid and can generate postman/openapi/python/go/node/java...
  - Combine the generated code with our Go SDK and run unit tests.
  - Combine the generated code with our Go SDK and run use-case regression tests.
  - Combine the generated code with our Python SDK and run unit tests.
  - Combine the generated code with our Python SDK and run use-case regression tests.
  - Publish the open api spec to our test readme.com project
  - If this is the 'main' branch
    - Publish the open api spec to our production readme.com project
- preview-docs
  - Generate a preview of the fern docs
- publish-prod-docs
  - Publish our docs to documentation.sayari.com

Schedule Updates: scheduled-updates.yaml (Runs every week day or on manual trigger)
- Check-for-updates
  - Check if ontology or risks have been updated
  - If so, regenerate code
  - Open a PR with the updates into this repo
- Update go/Python
  - If there were updates, regenerate the go and python
  - Open PRs in their respective repos
