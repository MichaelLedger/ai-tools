# Build the active Xcode scheme

Build the current project and report only what matters.

1. Use the `xcode-tools` MCP `BuildProject` tool to build the active scheme. If that server is unavailable, say so and stop rather than falling back to a raw `xcodebuild` invocation that may target the wrong scheme.
2. If the build succeeds with no warnings, reply with a single line confirming success and the scheme name.
3. If the build fails, call `GetBuildLog` and report:
   - The root-cause error first, with file and line.
   - Any other distinct errors, deduplicated. Do not paste repeated template instantiation noise.
   - Your diagnosis of the failure class: code error, signing, SPM resolution, missing file reference, or Swift version mismatch.
4. If the build succeeds but produces warnings, list only warnings introduced by recent changes. Ignore pre-existing warnings in vendored or generated code.
5. Propose a fix, but do not apply it unless I ask.

Keep the response short. I want the signal from the build log, not the log itself.
