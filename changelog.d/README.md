# Changelog fragments

Each pull request adds **one file** here instead of editing `CHANGELOG.md`, so open pull requests never
conflict on the changelog.

- File name: `<issue>.<section>.md`, e.g. `12.added.md`, `8.fixed.md`.
  `<section>` is one of `added`, `changed`, `deprecated`, `removed`, `fixed`, `security`
  ([Keep a Changelog](https://keepachangelog.com/en/1.1.0/)).
- Content: one line of English describing the change for users, ending with the issue number.
- At release time the fragments are collected into `CHANGELOG.md` under the new version and deleted.
