---
name: tea
description: >-
  Recover a filtered pipeline's exact stdin without rerunning it; tea caches
  each stage and leaves a pointer on stderr.
---

# tea logs

`tea` caches every wrapped filter's stdin (`grep`, `sort`, `rg`, and similar)
before it is gone. Watch command stderr for a line like:

```
[tea] --id N /tmp/….tea | <command>
```

That line identifies the cached input. When you need it:

1. Read `[tea]` lines from tool stderr or the slow-command hook context.
2. Open the logfile, or run `tea last`, `tea show [id]`, or `tea list`.
3. Prefer the capture over rerunning a long or expensive pipeline.
