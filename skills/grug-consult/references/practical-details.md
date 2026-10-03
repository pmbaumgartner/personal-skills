# Practical details

Apply these Grug-inspired preferences when relevant, not as mandatory architecture or instrumentation.

## Production diagnostics

Make important execution paths explainable through logs. For requests spanning services, use correlation IDs to connect events. Where useful, allow log levels to change without redeploying and diagnostics to target a particular user or request.

Invest in debugging tools before an incident: conditional breakpoints, expression evaluation, and stack navigation can replace guesswork. Logging infrastructure deserves similar attention.

Apply this advice within privacy and security constraints: targeted diagnostics should not expose secrets or unnecessary personal data.

## Frontend architecture

For content sites and straightforward forms, consider server-rendered HTML before a separate SPA and API. Splitting frontend and backend adds boundaries, network interactions, and tooling that must earn their maintenance cost.

Rich client-side interaction or established constraints may justify a SPA. Recommend from the application's needs, not loyalty to a framework; Grug's own libraries are examples, not required choices.

## API ergonomics

Start with what the caller wants to accomplish. Avoid forcing common tasks through internal concepts, conversions, or configuration machinery.

Offer a simple path with sensible defaults and a more explicit path for advanced needs. In object-oriented APIs, put common operations on the objects callers already use when that improves discoverability.

Do not hide consequential choices merely to shorten a call. A convenient API should reduce incidental work, not conceal necessary control.
