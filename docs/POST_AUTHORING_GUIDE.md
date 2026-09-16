# Technical post authoring guide

## Purpose

This blog is a searchable record of verified operational knowledge. Write for the
engineer who has the same incident later: they should be able to identify whether the
case matches their environment, apply a safe remedy, and verify the result.

## Recommended structure

Use only the sections that help the reader; do not add empty headings.

1. **Overview** — one to three sentences: what happened, impact, and the conclusion.
2. **Environment / scope** — product and version, topology, and assumptions. Redact
   customer names, hostnames, addresses, tickets, credentials, and private URLs.
3. **Symptom** — observable behaviour and the smallest relevant log or command output.
4. **Diagnosis** — evidence, hypotheses, and how the cause was narrowed down.
5. **Resolution** — exact, ordered actions plus rollback or operational cautions when
   applicable.
6. **Verification** — command, screen, metric, or expected result that proves success.
7. **References** — primary documentation, bug IDs, or reproducible source material.

## Formatting conventions

- Make the title describe the product area and the reader's problem. Keep the existing
  bracket taxonomy (for example `[WebLogic/SSL]`) so URLs and browsing habits remain
  predictable.
- Use `##` for major sections and `###` for steps within them. The Jekyll heading
  offset renders these at the appropriate visual level.
- Use fenced code blocks with a language whenever known (`bash`, `xml`, `java`,
  `text`). Keep only the lines needed to diagnose or reproduce the case.
- Use a list for prerequisites, options, and procedures; use a table only for compact
  comparisons.
- Intentional `<br>` spacing is allowed for Typora source readability. Do not use it
  inside fenced code blocks, lists, tables, or blockquotes, and prefer a new paragraph
  where the text is a distinct idea.
- Store new images at `assets/posts/images/<Category>/<slug>/` and link them with a
  root-relative `/assets/...` path.

## Publishing checklist

- Check that the title, date, tags, and category are accurate and that the public URL
  remains stable.
- Separate confirmed facts from hypotheses and include a verification step for product
  behaviour claims.
- Run `python tools/blog_audit.py`; resolve duplicate URLs, local image paths, missing
  assets, and possible secrets before publishing.
- Preview in both light and dark mode, including on a narrow screen.
