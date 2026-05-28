# Arkitektum Mandatory Instructions

## Package and Library Selection

Always prefer large, well-maintained, and official packages and libraries in all languages. Choose packages that are:
- Published by the official maintainers of the technology (e.g., AWS SDK by Amazon, Azure SDK by Microsoft)
- Widely adopted with active maintenance and regular releases
- Well-documented with strong community support

## Adding Third-Party Dependencies

**MANDATORY: never add a third-party package to a project without explicit user confirmation.** This applies to every ecosystem (pip/uv, npm, cargo, NuGet, go) and every manifest (`pyproject.toml`, `package.json`, `Cargo.toml`, `*.csproj`, `go.mod`).

Before asking the user, run the `check-package` skill to fetch the current version and license. Do not pin a version from memory. Examples:

- `check-package pypi requests`
- `check-package npm @tanstack/react-query`
- `check-package cargo serde`
- `check-package nuget Newtonsoft.Json`
- `check-package go github.com/gorilla/mux`

Then present the package, version, and license to the user and wait for confirmation.

License policy:

- **Preferred (permissive)**: MIT, Apache-2.0, BSD-2-Clause, BSD-3-Clause, ISC, MPL-2.0.
- **Acceptable, but mention the copyleft implication**: GPL-2.0, GPL-3.0, LGPL.
- **DO NOT ADD**: any NonCommercial license (CC-BY-NC and variants). Hard no, propose an alternative.
- **Strongly flag, require explicit override from the user**:
  - AGPL (any version) -- network copyleft.
  - BUSL (Business Source License) -- source-available, restricts commercial/competing use.
  - Other source-available non-OSI licenses (SSPL, ELv2, etc.).
- **`UNKNOWN` / missing license**: do not add. Ask the user to research the actual license status (check the project repository, `LICENSE` file, README, or homepage) and report back. In parallel, suggest one or two well-licensed alternatives that solve the same problem.

## Restricted Tools and Operations

- The `gh` CLI is not available locally -- do not attempt to use it.
- The `az` CLI is not available locally -- do not attempt to use it.
- Never run Terraform commands for infrastructure changes (`terraform apply`, `terraform destroy`, etc.).
- Never interact with production databases directly (no queries, migrations, or data modifications).

If you need output from any of these tools, ask the user to run the command and provide the result.

## Git Operations

- Never run `git push`, `git push --force`, or any variant. Let the user handle all push operations.
- Never run `git clean` -- the working directory may contain untracked files from other work in progress.
- Never run broad `git checkout .` or `git checkout -- .` to revert changes. Instead, revert surgically per file (e.g., `git checkout -- path/to/file1 path/to/file2` or `rm path/to/file1 path/to/file2`). The user may have other uncommitted changes you are not aware of.
- When the user says "revert", they mean undo the changes you made to files -- do this by re-editing the files back to their previous content. If the changes are too substantial to confidently re-edit by hand, confirm the approach with the user first. Do not use git commands to revert unless the user explicitly asks for it.

## Data Handling

- Never include real or production data, PII, or customer data in code, tests, comments, or log statements.
- Use synthetic or mock data for examples and tests.

## Security

- Do not use direct API calls (`curl`, `wget`, `fetch`, or SDK clients) to GitHub or Azure APIs as a workaround for CLI restrictions.
- Do not read or display contents of credential or token files (e.g., `~/.config/gh/`, `~/.azure/`, `~/.kube/config`, `~/.docker/config.json`). Never include secrets, tokens, or connection strings in code suggestions or command output.
- Do not attempt to install restricted CLIs (`gh`, `az`, `terraform`) or other infrastructure tools.

## Environment Files and Secrets

Do not attempt to read `.env` files -- they are not available locally. References to `.env` files are fine, but they must point outside the project folder (e.g., `~/.env/project-name` or a system-level path). If you find `.env` files or secrets stored inside the repository, advise the user to move them outside the project and use a secrets manager or environment variable injection from CI/CD.
