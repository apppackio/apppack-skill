# This is a just file that uses just to run commands.
# Documentation: https://github.com/casey/just

cli_reference := "skills/apppack/references/cli.md"

@_default:
    just -l

# Regenerate the CLI reference from the installed apppack binary
cli-docs:
    #!/usr/bin/env bash
    set -euo pipefail
    command -v apppack >/dev/null || {
        echo "error: apppack not on PATH — brew install apppackio/apppack/apppack" >&2
        exit 1
    }
    tmp=$(mktemp -d)
    trap 'rm -rf "$tmp"' EXIT
    apppack docgen --directory "$tmp" >/dev/null
    python3 scripts/gen_cli_reference.py "$tmp" --output {{ cli_reference }}

# Fail if the committed CLI reference is stale against the installed apppack
check-cli-docs: cli-docs
    #!/usr/bin/env bash
    set -euo pipefail
    if ! git diff --quiet -- {{ cli_reference }}; then
        echo >&2
        echo "error: {{ cli_reference }} is out of date for apppack $(apppack version | head -1)." >&2
        echo "Run 'just cli-docs' and commit the result." >&2
        echo >&2
        git --no-pager diff -- {{ cli_reference }} >&2
        exit 1
    fi
    echo "CLI reference is current for apppack $(apppack version | head -1)"

# Validate the plugin and marketplace manifests
validate:
    claude plugin validate . --strict

# Everything CI runs
check: validate check-cli-docs
