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

- `api_token`: This is how you'll specify your PAT (personal access token) for authentication purposes
- `organization_id`: This is your organization ID within the Censys Platform which is used alongside your PAT to authenticate a request
- `base_url` (optional): This is used to define the base URL (protocol and domain) through which the Censys Platform API should be accessed

To specify these config values, create a `test_asset.json` file in the base directory of this repository, then populate the fields as appropriate.

### Testing Locally

Testing is facilitated by using the `splunk-soar-sdk` tool, installed above. We recommend following the [SDK instructions](https://phantomcyber.github.io/splunk-soar-sdk/getting_started/testing_and_building.html#running-from-the-command-line) for running actions via the CLI as the primary development workflow, using a SOAR Cloud/on-prem instance just as a final verification step.

Parameters to the actions are passed via a JSON params file. You can create a `test_params.json` file in the base directory of this repository and it will be excluded from source control. You can create multiple param files (such as for each action) by following the pattern `test_params_{name}.json`.

To run a particular action via the CLI, invoke the add-on via Python directly:

```bash
python -m src.app action lookup_host -p test_param_host_.json -a test_asset.json
```

### Actions

These are the available base commands. To run one successfully, you will still need an appropriate asset file (specified with `-a`) and param file (specified with `-p`) as mentioned above.

| Action | CLI Command | Description | Docs |
|----|----|----|----|
| `lookup_host` | `python -m src.app action lookup_host` | Retrieves a host by IP lookup | [Host Definitions](https://platform.censys.io/home/definitions?resource=host) |
| `lookup_cert` | `python -m src.app action lookup_cert` | Retrieves a certificate by SHA256 lookup | [Cert Definitions](https://platform.censys.io/home/definitions?resource=cert) |
| `lookup_web_property` | `python -m src.app action lookup_web_property` | Retrieves a web property by `hostname:port` lookup | [Web Property Definitions](https://platform.censys.io/home/definitions?resource=cert) |
| `search` | `python -m src.app action search` | Performs a search across all Censys assets using the given query | [Search Result Docs](https://docs.censys.com/reference/v3-globaldata-search-query) |
| `test_connectivity` | `python -m src.app action test_connectivity` | Tests whether the asset file is sufficient to connect to the API | _N/A_ |

To add a new action, create a new file in `actions` with the same name as the search. Once it is ready to be tested, update `actions/registration.py` to register the new action, providing useful short/long descriptions. Lastly, update the above table to include the new action.

### Helpful Resources

- [Censys Data Definitions](https://platform.censys.io/home/definitions)
- [Censys Platform API Docs](https://docs.censys.com/reference/get-started)
- [Censys Platform Python SDK](https://pypi.org/project/censys-platform/)
- [Splunk SDK Docs](https://phantomcyber.github.io/splunk-soar-sdk/getting_started/)
- [uv docs](https://docs.astral.sh/uv/)

## License

[![Apache 2](https://img.shields.io/badge/license-Apache%202.0-orange.svg?style=flat-square)](http://www.apache.org/licenses/LICENSE-2.0)
