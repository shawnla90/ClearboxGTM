# Releasing

New skills, playbooks, and proof drops ship as tagged GitHub Releases, so anyone watching or starring the repo gets notified. This is the honest native reach: GitHub does not expose stargazer emails, and issues do not notify stargazers, so Releases are how a new drop reaches the people who starred. The steps:

1. Run the scan gate: **every release passes the VERIFYING.md scan gate before the tag is pushed.** No exceptions.
2. Update `CHANGELOG.md`: add a new version block at the top (newest first) describing what shipped.
3. Commit and push `main` first, then tag the pushed commit:
   ```bash
   git push origin main
   git tag -a v0.3.0 -m "The flagship drop"
   git push origin v0.3.0
   git rev-parse 'v0.3.0^{commit}'   # must equal origin/main
   ```
4. Cut the release from the tag, using the changelog block as the notes:
   ```bash
   # notes = the top version block of CHANGELOG.md
   awk '/^## \[/{c++} c==1{print} c==2{exit}' CHANGELOG.md > /tmp/notes.md
   gh release create v0.3.0 --title "v0.3.0 - The flagship drop" --notes-file /tmp/notes.md
   ```

The `.github/workflows/release-on-drop.yml` workflow drafts a release automatically when `skills/`, `playbooks/`, `engine/`, `proof/`, `transparency/`, or `CHANGELOG.md` change on `main`. A draft does not notify anyone until a human clicks publish, so you always get a review step. If the workflow already drafted the release, publish it with `gh release edit v0.3.0 --draft=false` instead of creating a second one.

Watchers who chose "Releases" get an email. Stargazers see the release in their GitHub home feed. To catch them yourself: **Watch, then Custom, then Releases**.

Versioning: MAJOR for a breaking restructure, MINOR for a new skill, playbook, or track, PATCH for fixes.
