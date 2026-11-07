---
name: roborev-analyze-test-fixtures
description: "Find reusable test fixtures, builders, and helpers to reduce duplication. Use for roborev test-fixtures analysis."
---

# Roborev: Test Fixtures

Read the files in the scope requested by the user before applying the instructions below. Report findings; do not modify code unless the user asks for changes.

Source: [test_fixtures.txt](https://github.com/kenn-io/roborev/blob/0cc4d482018fb022341adbdd84ff1e6c23a14083/internal/prompt/analyze/test_fixtures.txt). The upstream prompt below is preserved verbatim.

## Instructions

Analyze the test file(s) for opportunities to reduce duplication and improve maintainability through reusable test fixtures and helper functions.

Your task:
1. Read the test file(s) thoroughly
2. Identify:
   - Repeated test data construction
   - Common setup/teardown patterns
   - Similar assertion sequences
   - Mock objects or fakes created multiple times
   - Any boilerplate that appears across multiple tests
3. Propose concrete fixtures, builders, or helper functions that would simplify these tests
4. Note patterns that likely appear in other test files too

Output format:
- **PATTERNS FOUND:** Specific duplications with file names and line numbers
- **PROPOSED FIXTURES:** Concrete helper functions/fixtures to create, with example signatures
- **CROSS-FILE POTENTIAL:** Patterns likely shared across the codebase
- **PRIORITY:** High/Medium/Low based on code reduction potential
