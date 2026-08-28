# mcp2wup

Serwer MCP (stdio) — cienkie wrappery DSL.

```bash
mcp2wup serve
```

Narzędzia zapisujące, generujące i wykonujące DSL są domyślnie zablokowane.
Uruchom serwer z `WUP_MCP_ALLOW_MUTATION=1`, aby jawnie włączyć te operacje dla
zaufanych klientów MCP. Zapytania, walidacja, health i status pozostają dostępne.

Narzędzia: `wup_run_command`, `wup_run_dsl`, `wup_to_dsl`, `wup_query`, `wup_validate`, …
