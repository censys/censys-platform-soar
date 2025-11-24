# Censys Platform for Splunk

This app implements investigative actions to get information from the public [Censys Platform API](https://docs.censys.com/reference/get-started) into [Splunk SOAR](https://www.splunk.com/en_us/products/splunk-security-orchestration-and-automation.html).

## Getting Started

### Prerequisites

1. You are using a Mac or Linux machine (the Splunk SDK does not support Windows)
1. `git` is available in your CLI

### Installation

1. Install [uv](https://docs.astral.sh/uv/), which is our Python dependency/environment manager
1. Using `uv`, install Python `3.14` (`uv python list` → `uv python install [version_you_choose]`)
1. Install the `splunk-soar-sdk` as a `uv` tool: `uv tool install splunk-soar-sdk`
1. Install the linting/pre-commit tools: `uv tool install ruff` and `uv tool install pre-commit --with pre-commit-uv`
1. Install the project's dependencies: `uv sync`

### Configuration

It is recommended that, when developing, you use the Python environment managed by `uv`. You can do this by running `source ./.venv/bin/activate` in the base directory of this repository once the installation steps above are complete.

Add-on settings are managed through the SDK's [Asset Configuration](https://phantomcyber.github.io/splunk-soar-sdk/getting_started/defining_asset.html) definitions. The configuration exposed by the add-on includes:

- `base_url`: This is used to define the base URL (protocol and domain) through which the Censys Platform API should be accessed
- `api_token`: This is how you'll specify your PAT (personal access token) for authentication purposes
- `organization_id`: This is your organization ID within the Censys Platform which is used alongside your PAT to authenticate a request

### Testing Locally

Testing is facilitated by using the `splunk-soar-sdk` tool, installed above. We recommend following the [SDK instructions](https://phantomcyber.github.io/splunk-soar-sdk/getting_started/testing_and_building.html#running-from-the-command-line) for running actions via the CLI as the primary development workflow, using a SOAR Cloud/on-prem instance just as a final verification step.

To run a particular action via the CLI, invoke the add-on via Python directly:

```bash
python src/app.py action my-action -p test_params.json -a test_asset.json
```

### Helpful Resources

- [Censys Platform API Docs](https://docs.censys.com/reference/get-started)
- [Censys Platform Python SDK](https://pypi.org/project/censys-platform/)
- [Splunk SDK Docs](https://phantomcyber.github.io/splunk-soar-sdk/getting_started/)
- [uv docs](https://docs.astral.sh/uv/)

## License

[![Apache 2](https://img.shields.io/badge/license-Apache%202.0-orange.svg?style=flat-square)](http://www.apache.org/licenses/LICENSE-2.0)
