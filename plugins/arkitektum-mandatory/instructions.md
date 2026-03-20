# Arkitektum Mandatory Instructions

## Package and Library Selection

Always prefer large, well-maintained, and official packages and libraries in all languages. Choose packages that are:
- Published by the official maintainers of the technology (e.g., AWS SDK by Amazon, Azure SDK by Microsoft)
- Widely adopted with active maintenance and regular releases
- Well-documented with strong community support

If no official package exists for a given need, or you want to suggest a third-party alternative, always ask the user to confirm before adding it as a dependency.

## Dependency Licenses

When adding new dependencies, check and report the license. Flag dependencies with AGPL, NonCommercial (e.g., CC BY-NC), or missing/unknown licenses -- these can be problematic. Point out GPL dependencies as they have copyleft implications, but they are acceptable. Prefer dependencies with permissive licenses (MIT, Apache 2.0, BSD).

## Restricted Tools and Operations

- The `gh` CLI is not available locally -- do not attempt to use it.
- The `az` CLI is not available locally -- do not attempt to use it.
- Never run Terraform commands for infrastructure changes (`terraform apply`, `terraform destroy`, etc.).
- Never interact with production databases directly (no queries, migrations, or data modifications).

If you need output from any of these tools, ask the user to run the command and provide the result.

## Git Operations

- Never run `git push`, `git push --force`, or any variant. Let the user handle all push operations.

## Data Handling

- Never include real or production data, PII, or customer data in code, tests, comments, or log statements.
- Use synthetic or mock data for examples and tests.

## Security

- Do not use direct API calls (`curl`, `wget`, `fetch`, or SDK clients) to GitHub or Azure APIs as a workaround for CLI restrictions.
- Do not read or display contents of credential or token files (e.g., `~/.config/gh/`, `~/.azure/`, `~/.kube/config`, `~/.docker/config.json`). Never include secrets, tokens, or connection strings in code suggestions or command output.
- Do not attempt to install restricted CLIs (`gh`, `az`, `terraform`) or other infrastructure tools.

## Environment Files and Secrets

Do not attempt to read `.env` files -- they are not available locally. References to `.env` files are fine, but they must point outside the project folder (e.g., `~/.env/project-name` or a system-level path). If you find `.env` files or secrets stored inside the repository, advise the user to move them outside the project and use a secrets manager or environment variable injection from CI/CD.
