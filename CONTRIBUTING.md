# Contributing to Tucuxi-Drugs

Thank you for your interest in contributing! This document describes the conventions and workflow expected from contributors.

Full documentation is available in the [`docs/`](docs/) folder and online at https://tucuxi-cdss-core.readthedocs.io/en/latest/.

---

## Table of Contents

- [Branching and Workflow](#branching-and-workflow)
- [Commit Messages](#commit-messages)
- [Code Style](#code-style)

---

## Branching and Workflow

When adding a new drug model, do the following:
- Create a feature branch off `dev`:
  ```sh
  git checkout -b dev-<drugid>.<author><year>
  ```
- Work on this branch until everything goes well
- Open a pull request against `dev` with a clear description of what the change does and why.

When working on something else:

- Target branch for contributions: `dev` (or the branch specified in the issue/PR).
- Create a feature or fix branch off `dev`:
  ```sh
  git checkout -b feat/my-feature
  ```
- Keep commits focused and atomic. One logical change per commit.

The maintainer is responsible for merging `dev` to `main` when relevant.

---

## Commit Messages

Commit messages must follow the [Conventional Commits](https://www.conventionalcommits.org/) specification. The **commit-msg** hook installed by `setup` enforces this automatically.

### Format

```
type(scope)?: subject
```

- **type** — one of: `build`, `chore`, `ci`, `docs`, `feat`, `fix`, `perf`, `refactor`, `revert`, `style`, `test`
- **scope** — optional, lowercase, e.g. `flow`, `exporter`, `query`
- **subject** — imperative mood, no trailing period

### Examples

```
feat(exporter): add JSON report export
fix(flow): handle null dose in pipeline
docs: update building instructions in README
refactor(query)!: rename XpertQueryData fields

BREAKING CHANGE: XpertQueryData::getDrug() renamed to getDrugModel()
```

### Rules

- The header must match `type(scope)?: subject` exactly.
- Breaking changes require a `!` after the type/scope **and** a `BREAKING CHANGE: ...` footer.
- Merge commits are exempted from validation automatically.

---

## Code Style

### Naming Conventions

The naming convention is:

```
ch.tucuxi.<drugname>.<firstauthor><year>.tdd
```

For specific sub-models (for instance with different targets):

```
ch.tucuxi.<drugname>.<firstauthor><year>-<something>.tdd
```

---

## Git Hooks

The hooks in `scripts/hooks/` are installed into `.git/hooks/` by `./scripts/linux/run setup`.

| Hook | Purpose |
|------|---------|
| `commit-msg` | Rejects commit messages that do not follow the Conventional Commits format |

If a commit is rejected, fix the reported issue and recommit. Do **not** bypass hooks with `--no-verify` unless there is a documented exceptional reason.

---

## Submitting Changes

3. Open a pull request against `main` with a clear description of what the change does and why.
4. Reference any related issue in the PR description (e.g., `Closes #42`).
5. Add yourself to [CONTRIBUTORS.md](CONTRIBUTORS.md) if this is your first contribution.
