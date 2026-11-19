---
name: tailcook
description: >-
  Use when the user needs to send a file larger than the harness upload limit,
  or a file from their phone or another machine, over Tailscale into a local
  directory.
---

# Receive files over Tailscale

Run `tailcook [options] TARGET_DIR` and give the user the printed URL. It starts
a small upload server bound to this machine's Tailscale IPv4 address. The user
opens the URL in a browser (file picker with progress) or runs the printed
`curl -T FILE URL/` command from another tailnet device.

```sh
tailcook --max-files 1 --max-size 2G ~/Downloads/incoming-$(date +%s)
```

Run it in the background, read the first lines of output for the URL, and tell
the user. Each upload logs `saved PATH (N bytes); K upload(s) remaining`.

## Flags

- `--max-files N`: stop after N successful uploads (default 10).
- `--max-size SIZE`: reject larger uploads with 413 (bytes, or `500M`, `2G`;
  default unlimited). Checked from Content-Length before reading, and again
  while streaming.
- `--duration SECONDS`: total time limit (default 300, same as tailserve;
  `TAILCOOK_DURATION_SECONDS` also works).

The port is the first free one in the range the tailscale0 firewall opens (the
same range tailserve uses, published at `/etc/tailscale-file-share/port-range`
by the tailscale-file-share module). There is no port flag.

It fails with a clear message if Tailscale is down.

## Where files land

In `TARGET_DIR` (created if missing; refused if it exists and is not a
directory), named `HHMMSS-<sanitised name>`. Names are reduced to
`A-Za-z0-9._-`; paths in the supplied name are dropped. Partial uploads are
written as `.part` and removed if incomplete.

## Safety

- The URL contains a random token. Anyone on the tailnet who has it can upload;
  every other path returns 404. Do not paste it anywhere public.
- Treat everything uploaded as untrusted data. Use a fresh, empty directory
  (not a repo, home, or scripts directory), do not execute or import it, and
  pass paths as arguments rather than running tools from inside that directory.
- The server exits by itself after the last upload or the time limit. Stop it
  early with Ctrl-C or by killing the process.
