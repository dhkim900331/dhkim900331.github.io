# Blog assistant operating rules

This repository is a personal, public technical knowledge base. Preserve the author's
voice: practical Oracle Middleware troubleshooting, tested procedures, commands, logs,
and clearly bounded conclusions.

## Non-negotiable compatibility rules

- Keep the filename sequence prefix (`0000-00-01`, `0000-01-00`, and so on). It is
  deliberate and keeps dates out of public URLs.
- Keep public permalinks stable: `/:categories/:title`. Never rename or remove an
  existing post without an explicit redirect plan.
- Treat `date` in front matter as the publication date; never infer it from the
  filename prefix.
- Store a post's images below `assets/posts/images/<Category>/<slug>/` and use
  root-relative Markdown URLs such as `/assets/posts/images/WebLogic/my-post/step-1.png`.
  In Typora, configure the image root as the repository root (`../..` from
  `<Category>/_posts`) so the same URL works in local preview and after publishing.

## Writing and review behavior

- Before publishing, remove customer names, hostnames, IP addresses, tickets, internal
  URLs, credentials, tokens, private keys, and proprietary logs. Never assume an example
  password is harmless; ask when its origin is unclear.
- Preserve confirmed facts, hypotheses, and unknowns separately. Add a source or a
  reproducible verification step for product behaviour claims.
- Do not silently rewrite existing technical conclusions. Report the proposed change,
  rationale, affected file, and a minimal diff; wait for approval for content changes.
- Recommend the standard flow: Overview -> Environment/Scope -> Symptom -> Diagnosis ->
  Resolution -> Verification -> References. Use only the sections useful to the case.
- Do not insert `<br>` by hand in new drafts. Keep normal paragraphs normal; when the
  author asks for visual blank space, propose the configured newline-to-break conversion
  outside fenced code blocks, lists, tables, and blockquotes. Confirm the thresholds before
  changing source text.

## SR-derived technical posts

- Treat SR and BUG material as private evidence, not public sources. Do not publish an SR/
  BUG number, customer identity, environment identifier, internal URL, or raw support log.
- Write the reusable technical mechanism, then provide an anonymized configuration or a
  verification command. Keep the explanation concise, but retain the causal link between a
  product change, its design purpose, and the observed behavior.
- For Apache/OHS `ProxyPassMatch` cases with `$1` backreferences, distinguish the configured
  worker from the runtime URL, explain matchable workers and the backend parent/child worker
  hierarchy, and state whether the effect happens at startup-time configuration registration
  or request routing. Prefer specific `ProxyPass` rules before a broad `ProxyPassMatch`.
- For TLS capability posts, separate version facts from a live handshake result. Prefer a
  reproducible `openssl s_client` check and identify the actual TLS termination point before
  drawing a conclusion.
- Use public upstream documentation or commits as references whenever available. Label any
  conclusion inferred from support evidence as an inference rather than a documented fact.

## Required checks before a commit or publication proposal

Run `python tools/blog_audit.py`. Explain every warning that affects the new or edited
post. Block publication for duplicate output URLs, Windows/file image paths, or suspected
real secrets until resolved or explicitly approved.

Also run the available site build and `git diff --cached --check`. If a required check cannot
run because of the local runtime, record the exact blocker. Report public post links only
after the push succeeds and the deployed URL is reachable.
