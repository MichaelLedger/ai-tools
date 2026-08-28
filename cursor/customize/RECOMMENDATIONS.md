# Cursor Customization Pick List — Senior iOS Engineer

Tick the items you want, and I'll install/scaffold them into `cursor/customize/` and your Cursor config.

Environment detected: macOS 26.5.1 · Xcode 26.6 · `mcpbridge` available · `swiftlint` + `swiftformat` installed · `uvx` **not** installed.

Priority key: **P0** = install first · **P1** = strong value · **P2** = nice to have

---

## 0. Current state

| Category | Installed today |
|----------|-----------------|
| Plugins | figma, github, atlassian, superpowers |
| MCPs (plugin) | `plugin-figma-figma`, `plugin-github-github`, `plugin-atlassian-atlassian` |
| MCPs (user) | `Framelink Figma MCP`, `github`, `figma-2`, `mcp-atlassian`, `swift-version-server` |
| Rules | `new-file-copyright-header` (always), `figma-mcp` (globs) |
| Skills | generate-similar-photos, kekenet-friends-lesson, graphify (+ plugin & built-in skills) |
| Hooks | superpowers `sessionStart` only |
| Commands | none |
| Subagents | none |

Biggest gap: **no native Xcode/build/test integration**, and **no Swift-specific rules**.

---

## 1. MCP servers

### [x] P0 — `xcode-tools` (Apple's built-in Xcode MCP) — **installed**

The single highest-value addition. Gives the agent build, test, diagnostics, SwiftUI previews, and Apple docs search. Confirmed available at `/Applications/Xcode.app/Contents/Developer/usr/bin/mcpbridge`.

Tools include `BuildProject`, `GetBuildLog`, `RunAllTests`, `RunSomeTests`, `XcodeListNavigatorIssues`, `RenderPreview`, `DocumentationSearch`, `ExecuteSnippet`.

```json
"xcode-tools": {
  "command": "xcrun",
  "args": ["mcpbridge"]
}
```

Prerequisites: Xcode → Settings → Intelligence → enable **Xcode Tools MCP**; keep the target project open in Xcode.

Known issue: repeated macOS "Allow access to Xcode" prompts. If that becomes annoying, the broker-mode wrapper below helps.

### [ ] P2 — `mcpbridge-wrapper` (broker mode, only if `xcode-tools` is flaky)

Reduces reconnect churn and TCC prompt frequency. Requires installing `uv` first (`brew install uv`).

```json
"xcode-tools": {
  "command": "uvx",
  "args": ["--from", "mcpbridge-wrapper", "mcpbridge-wrapper", "--broker"]
}
```

### [x] P1 — Retire `swift-version-server` — **removed**

It only shells out to `swift --version`. Fully superseded by `xcode-tools`. Removing it reduces startup noise.

### [x] P1 — Consolidate the three Figma MCPs — **`figma-2` removed**

You run `plugin-figma-figma` (OAuth), `Framelink Figma MCP` (npx), and `figma-2` (local script). Suggested: keep the plugin as primary, keep Framelink for quick read/export, drop `figma-2`.

### [x] P1 — Retire the Docker `mcp-atlassian` — **removed**

The Atlassian plugin gives the same Jira/Confluence coverage over OAuth, with no Docker and no API token sitting in `mcp.json`.

### [ ] P2 — Sentry MCP (only if your team uses Sentry)

Pull crash groups and stack traces into the agent's context when triaging iOS crashes.

---

## 2. Plugins

The Cursor marketplace currently ships four first-party plugins, and **you already have all four**. There is no dedicated iOS plugin yet; `xcode-tools` fills that role.

### [ ] P2 — Audit the Atlassian plugin

Keep only if you actively use Jira/Confluence from the editor. Each enabled plugin adds tool-listing overhead to every session.

---

## 3. Rules (`.mdc`)

All below are scoped with `globs` so they only load for Swift work. Suggested destination: `cursor/customize/Rules/`, then symlink into each iOS repo.

### [x] P0 — `swift-concurrency.mdc` — **installed**

`@MainActor` for UI state, structured concurrency over raw GCD, no blocking the main thread, `Sendable` boundaries, avoiding actor reentrancy bugs.

### [x] P0 — `swift-memory.mdc` — **installed**

`[weak self]` in escaping closures that outlive the owner, when `unowned` is actually safe, retain-cycle patterns in Combine/delegates/notification observers.

### [ ] P1 — `ios-architecture.mdc`

Encode your team's layering (e.g. View → ViewModel → Service), no business logic in SwiftUI `body`, dependency injection over singletons.

### [ ] P1 — `swift-testing.mdc`

New logic requires unit tests; UI tests reserved for critical flows; protocol-based injection for testability; XCTest vs Swift Testing naming conventions.

### [ ] P1 — `xcode-project-hygiene.mdc`

Don't hand-edit `project.pbxproj` unless required; SPM first; pin versions in `Package.resolved`; never commit `xcuserdata`.

### [ ] P2 — `ios-accessibility.mdc`

Accessibility labels, Dynamic Type support, 44pt minimum tap targets, VoiceOver ordering.

### [ ] P2 — `objc-swift-interop.mdc`

Relevant for your mixed codebases (`PRTBusinessUnit`, `freeprints_ios_*`): nullability annotations, `NS_SWIFT_NAME`, bridging header discipline.

### [ ] P2 — Tighten `figma-mcp.mdc`

Its globs are web-only (`.tsx`, `.jsx`, `.css`). Add `**/*.swift` if you want it active during SwiftUI design work, or leave as-is to save context.

---

## 4. Skills

### Already available — just use them

| Skill | Source | Use when |
|-------|--------|----------|
| `figma-swiftui` | figma plugin | SwiftUI ↔ Figma, either direction |
| `systematic-debugging` | superpowers | Any bug, before proposing fixes |
| `test-driven-development` | superpowers | New non-trivial logic |
| `verification-before-completion` | superpowers | Before claiming done / opening a PR |
| `requesting-code-review` | superpowers | Before merge |
| `review-bugbot` | built-in | Pre-PR local review |
| `split-to-prs` | built-in | Change grew too large |

### [x] P0 — Author `ios-swift-conventions` skill — **installed (has TODOs to fill in)**

The highest-leverage custom item. Encodes *your team's* decisions rather than generic Swift advice: module layout, naming, error handling, logging, feature-flag patterns, PlanetArt/PRT-specific idioms.

### [ ] P1 — Author `xcode-build-triage` skill

A repeatable procedure: run `BuildProject`, read `GetBuildLog`, classify the failure (signing / SPM resolution / missing symbol / Swift version), then apply the standard fix for that class.

### [ ] P2 — Author `ios-release-checklist` skill

Version/build bump, changelog, screenshots, TestFlight upload, App Store metadata — whatever your actual release steps are.

---

## 5. Hooks

You have `swiftlint` and `swiftformat` installed, so these are ready to wire up. Destination: `~/.cursor/hooks.json` (global) or `<repo>/.cursor/hooks.json` (per project, checked into git).

### [x] P0 — `afterFileEdit` → swiftformat — **installed**

Auto-format every `.swift` file the agent edits. Eliminates an entire class of review noise.

### [ ] P1 — `afterFileEdit` → swiftlint (report only)

Surface lint violations back to the agent immediately so it self-corrects instead of you catching it in review.

### [ ] P1 — `beforeShellExecution` → guard destructive commands

Block or require confirmation on `rm -rf`, `git push --force`, `pod deintegrate`, and similar.

### [ ] P2 — `beforeSubmitPrompt` → secret scan

Warn if a prompt contains something matching `figd_`, `ATATT`, `ghp_`, etc. Directly relevant given what we found in your `mcp.json` earlier.

### [ ] P2 — `sessionStart` → project context

Echo current branch, Xcode version, and active scheme into the session so the agent starts oriented.

---

## 6. Commands (slash commands)

You have none. These are `.md` files in `~/.cursor/commands/` or `<repo>/.cursor/commands/`, invoked as `/name`.

### [x] P1 — `/build` — **installed**

Build the active scheme via `xcode-tools`, then summarize only the errors and warnings that matter. Requires the Xcode MCP.

### [x] P1 — `/test` — **installed**

Run the test suite, then report only failures with the relevant source lines.

### [ ] P2 — `/pr`

Generate a PR description from the branch diff using your team's template.

### [ ] P2 — `/jira`

Turn the current change into a Jira ticket via the Atlassian plugin.

### [ ] P2 — `/swiftcheck`

Run `swiftlint` + `swiftformat --lint` across changed files and summarize.

---

## 7. Subagents

You have none. These are `.md` files with frontmatter in `~/.cursor/agents/` or `<repo>/.cursor/agents/`. They run in isolated context, which keeps your main conversation clean.

### [x] P0 — `swift-reviewer` — **installed**

Reviews Swift diffs specifically for concurrency correctness, retain cycles, force-unwraps, main-thread violations, and API availability. Far more targeted than a generic reviewer.

### [ ] P1 — `xcode-build-fixer`

Given a failing build, reads the build log, isolates root cause, applies a minimal fix, rebuilds to confirm. Pairs with `xcode-build-triage`.

### [ ] P1 — `ios-explorer`

Navigates large mixed ObjC/Swift codebases and reports back a summary, so exploring `PRTBusinessUnit` doesn't flood your main context.

### [ ] P2 — `test-writer`

Given a Swift type, writes XCTest/Swift Testing cases covering the meaningful paths.

### [ ] P2 — `crash-triage`

Given a stack trace, locates the responsible code and proposes a fix. Best combined with the Sentry MCP.

---

## Suggested starter set

If you'd rather not pick individually, this is the highest-value bundle:

1. MCP: `xcode-tools`
2. Rules: `swift-concurrency`, `swift-memory`
3. Hook: `afterFileEdit` → swiftformat
4. Subagent: `swift-reviewer`
5. Skill: `ios-swift-conventions`
6. Cleanup: drop `swift-version-server` and `figma-2`

---

## How to reply

Either list the item names you want, or say "starter set", or mark the boxes in this file and tell me to read it.
