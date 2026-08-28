# Run the test suite

Run tests and report only failures.

1. Use the `xcode-tools` MCP tools. Prefer `RunSomeTests` scoped to the area I just changed; use `RunAllTests` only when I ask for a full run or when the change is broad. Call `GetTestList` first if you need to know what exists.
2. If everything passes, reply with one line: how many tests ran and how long it took.
3. For each failure, report:
   - Test name and the assertion that failed.
   - The relevant source lines from the test and from the code under test.
   - Whether the failure looks like a real regression, a flaky test (timing, ordering, network), or a stale expectation.
4. Group failures that share a root cause instead of listing them separately.
5. Propose a fix, but do not apply it unless I ask.

If the build fails before tests run, report it as a build failure and stop.
