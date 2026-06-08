# dsl2wup

Warstwa kontroli WUP — grammar DSL, JSON Schema, Protobuf, CQRS bus, EventStore.

Jedyny punkt mutacji: `dsl2wup.dispatch()`.

```bash
dsl2wup -c 'VALIDATE wup.yaml PROJECT .'
dsl2wup validate-schema
```
