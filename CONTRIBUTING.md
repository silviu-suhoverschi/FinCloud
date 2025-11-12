# Contributing to FinCloud

Thank you for your interest in contributing to FinCloud! This document provides guidelines and instructions for contributing.

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers and help them get started
- Focus on constructive feedback
- Respect differing viewpoints and experiences

## How to Contribute

### Reporting Bugs

1. Check if the bug has already been reported in [Issues](https://github.com/your-username/FinCloud/issues)
2. If not, create a new issue with:
   - Clear title and description
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, versions, etc.)
   - Screenshots if applicable

### Suggesting Features

1. Check existing feature requests
2. Create a new issue with the `enhancement` label
3. Describe the feature and its use case
4. Explain why it would be valuable

### Pull Requests

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Write or update tests
5. Ensure all tests pass
6. Update documentation
7. Commit with clear messages
8. Push to your fork
9. Open a Pull Request

## Development Setup

```bash
# Clone your fork
git clone https://github.com/your-username/FinCloud.git
cd FinCloud

# Install dependencies
cd services/budget-service
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Run tests
pytest

# Run linting
ruff check .
black --check .
```

## Code Style

### Python
- Follow PEP 8
- Use type hints
- Use `black` for formatting
- Use `ruff` for linting
- Write docstrings for functions and classes

### TypeScript/JavaScript
- Follow the project's ESLint configuration
- Use TypeScript for type safety
- Write JSDoc comments for complex functions

## Testing

- Write tests for new features
- Maintain or improve code coverage
- Run tests before submitting PR
- Include integration tests for API endpoints

## Documentation

- Update README if needed
- Document new features in `/docs`
- Update API documentation
- Include code comments for complex logic

## Commit Messages

Follow the conventional commits specification:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting)
- `refactor`: Code refactoring
- `test`: Test changes
- `chore`: Build/config changes

Examples:
```
feat(budget): add recurring transaction support
fix(portfolio): correct ROI calculation
docs(api): update authentication guide
```

## Review Process

1. Maintainers will review your PR
2. Address feedback and requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited

## Community

- Join discussions in [GitHub Discussions](https://github.com/your-username/FinCloud/discussions)
- Ask questions
- Share ideas
- Help others

## License

By contributing, you agree that your contributions will be licensed under the AGPL-3.0 License.

Thank you for contributing to FinCloud!
