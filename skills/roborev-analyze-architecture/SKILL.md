---
name: roborev-analyze-architecture
description: "Review module organization, dependency flow, and architectural boundaries. Use for roborev architecture analysis."
---

# Roborev: Architecture

Read the files in the scope requested by the user before applying the instructions below. Report findings; do not modify code unless the user asks for changes.

Source: [architecture.txt](https://github.com/kenn-io/roborev/blob/0cc4d482018fb022341adbdd84ff1e6c23a14083/internal/prompt/analyze/architecture.txt). The upstream prompt below is preserved verbatim.

## Instructions

Analyze the provided code for architectural patterns, design decisions, and structural improvements.

Your task:
1. Identify the overall architecture:
   - Package/module organization
   - Dependency flow and layering
   - Key abstractions and interfaces
   - Data flow patterns
2. Evaluate architectural qualities:
   - Separation of concerns
   - Coupling and cohesion
   - Testability
   - Extensibility
3. Find architectural issues:
   - Circular dependencies
   - Leaky abstractions
   - Inappropriate layering violations
   - Missing or redundant indirection

Output format:
- **ARCHITECTURE OVERVIEW:** Brief description of the current structure
- **STRENGTHS:** Good architectural decisions
- **CONCERNS:** Architectural issues or anti-patterns
- **RECOMMENDATIONS:** Specific improvements with rationale
- **DEPENDENCY MAP:** Key dependencies between components (if relevant)
