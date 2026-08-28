---
name: ios-swift-conventions
description: Team conventions for iOS and Swift work - module layout, naming, error handling, logging, dependency injection, and testing. Use when writing or reviewing Swift code, adding a new type or module, or deciding where code belongs.
---

# iOS / Swift Team Conventions

These are the defaults for this codebase. They override generic Swift advice.

> **Customize me.** Sections marked `TODO` are placeholders. Replace them with the real decisions for your projects (PRTBusinessUnit, freeprints_ios_*, synergy-ios) so the agent stops guessing.

## Architecture

Layering is **View → ViewModel → Service → Client**.

- Views render state and forward intent. No networking, persistence, or business rules in a SwiftUI `body` or a view controller.
- ViewModels are `@MainActor`, own presentation state, and expose it `private(set)`.
- Services hold business logic and are protocol-backed so they can be faked in tests.
- Clients wrap a single external dependency (HTTP, Keychain, Photos, CoreML).

Dependencies are injected through the initializer. Add a singleton only when the type genuinely models a process-wide resource, and say why in a comment.

## Module layout

TODO: describe how a feature is laid out in this repo, for example:

```
Sources/<Feature>/
  Views/
  ViewModels/
  Services/
  Models/
```

Shared code belongs in the appropriate SPM target, not copied between apps.

## Naming

- Types are nouns; protocols are either capability names (`Fetching`, `Cacheable`) or role names (`FeedService`).
- Do not prefix protocols with `I` or suffix implementations with `Impl`. Prefer `FeedService` / `LiveFeedService` / `StubFeedService`.
- Booleans read as assertions: `isEnabled`, `hasLoaded`, `shouldRetry`.
- Keep the existing Objective-C prefix (for example `PRT`) on types that must be visible to Objective-C; do not add it to pure Swift types.

## Error handling

- Model expected failures as `throws` with a typed domain error. Reserve optionals for genuine absence, not for failure.
- Never discard an error silently. If a `catch` is intentionally empty, log the reason.
- Surface user-facing errors through the ViewModel as presentation state, not by throwing into the view.

## Logging

TODO: confirm the logging stack. Default assumption is `OSLog`:

```swift
private let log = Logger(subsystem: "com.example.app", category: "Feed")
```

Never log tokens, personal data, or full request bodies.

## Concurrency and memory

See the `swift-concurrency` and `swift-memory` rules. Summary: isolation is declared on the type, `Task`s are cancelled, escaping closures capture `self` weakly.

## Dependencies

- SPM first. Add CocoaPods or Carthage only where a dependency offers no SPM support.
- Pin versions and commit `Package.resolved`.
- Do not hand-edit `project.pbxproj` unless there is no alternative; never commit `xcuserdata`.

## Testing

- New business logic ships with unit tests. Inject fakes through the protocol boundary rather than stubbing the network.
- UI tests cover critical flows only - they are slow and brittle.
- Test names state the behavior: `test_load_whenAPIFails_setsErrorState`.

TODO: state whether this codebase uses XCTest, Swift Testing, or both, and where test targets live.

## Accessibility and localization

- Every interactive element has an accessibility label.
- Support Dynamic Type; do not hard-code font sizes.
- Tap targets are at least 44x44 points.
- User-facing strings come from a strings catalog, never inline literals.
