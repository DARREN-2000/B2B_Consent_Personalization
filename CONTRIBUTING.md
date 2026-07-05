# Contributing to ConsentHub

First, thank you for your interest in contributing to ConsentHub! We welcome contributions from everyone—whether it's fixing a bug, adding a new feature, improving documentation, or creating tutorials.

## Code of Conduct

By participating in this project, you agree to abide by our [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting Started

1.  **Fork the repository** on GitHub.
2.  **Clone your fork** locally: `git clone https://github.com/YOUR-USERNAME/B2B_Consent_Personalization.git`
3.  **Set up your development environment** as described in the [Development Guide](docs/development.md).

## Development Workflow

1.  **Create a branch** for your feature or bug fix: `git checkout -b feature/my-new-feature`
2.  **Make your changes**. Ensure you write tests for any new logic (backend tests are in `backend/tests/`).
3.  **Run the test suite** locally before committing: `make test`
4.  **Format your code**: Ensure Python code adheres to PEP8.

## Submitting a Pull Request (PR)

1.  Push your branch to your fork: `git push origin feature/my-new-feature`
2.  Open a Pull Request against the `main` branch of the ConsentHub repository.
3.  Fill out the PR template completely. Provide context on *why* this change is needed and *how* it was tested.
4.  Wait for a maintainer to review your code. We try to review PRs within 48 hours.

## Reporting Bugs

If you find a bug, please use the Bug Report issue template. Provide as much detail as possible, including:
- Steps to reproduce
- Expected behavior
- Actual behavior
- Your environment (OS, Docker version, Python version, etc.)

## Requesting Features

To request a new feature, use the Feature Request issue template. Explain the problem you are trying to solve and how the proposed feature addresses it.