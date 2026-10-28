---
name: server-tour
description: Exercise this demo MCP server's tools, prompts, and resources to check that a client handles each feature. Use when testing an MCP client against this server.
---
# Server tour

Walk through the server's features in order and report what each one returned.

1. Call both versions of `echo` and confirm the client can tell v1 and v2 apart.
2. Call `add` with two small integers.
3. Call `form_elicitation` and fill in the form; then call `url_elicitation` and decline it.
4. Call `generate_sized_response` with `10KB`, then `1MB`.
5. Read `config://app` and `users://42/profile`.
6. Get the `greeting` prompt with any name.

Skip `sleep` and `error` unless the user asks for them: one never returns, the other always fails.

Use [checklist.md](checklist.md) to record results.
