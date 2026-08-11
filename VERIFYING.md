# Verifying

This repo makes public claims about a real system. This file is the standing loop that keeps those claims honest: where numbers are allowed to come from, what gets checked before every release, and how corrections turn into new rules.

## Provenance rule (numbers)

- **Only `proof/generate_proof.py` emits statistics.** No number about views, karma, posts, leads, wins, or signups is ever typed by hand into any file in this repo. Hand-typed stats drifted 2–5x from reality historically; generated stats cannot.
- Every stat block carries an `asOf` date. If `asOf` is **more than 14 days old, the stats are stale**: re-run the generator before citing or releasing anything that touches them.
- If a claim cannot be derived from a database query, it is either rewritten as qualitative language or cut. There is no third option.

## Language boundaries

- **Retrieval is not citation.** Exa-style search results measure `retrieval_visibility` — whether content surfaces when an index is queried. A *citation* claim requires a captured AI answer with a receipt (see `skills/reddit-agency/AI-VISIBILITY-SCORECARD.csv` for the receipt method). Never upgrade one into the other.
- The views claim is the string **"1.5M+"**, exactly. It does not round up. When the real number crosses the next million, update this rule first, then the generator, then the docs — in that order.
- **Automation boundaries** (see `playbooks/automation-boundaries.md`): research, classification, drafting, and monitoring can be automated; posting, voting, and DMs are always human actions. Docs must never imply otherwise.
- **Client-facing Plan Setup is outcome language.** Say that a separate client offer can be added and the client can pay for it. Do not expose payment-provider mechanics, admin emails or flags, internal workbook or workspace links, run IDs, or processor-specific setup in client-facing agency guidance.

## FACTCHECK gates

The onboarding skill ships with a six-rule gate (`skills/clearbox-onboard/FACTCHECK.md`): every selling point traces to a URL, competitor claims need a source on the competitor, unverifiable claims get cut. The same discipline applies to this repo's own docs.

**Corrections become rules.** When a published claim is found wrong, the fix is two commits: one correcting the claim, one adding a check to this file (or the scan gate below) that would have caught it. The gate only grows.

## Scan gate

Every release passes this gate **before the tag is pushed**. Run from the repo root. The never-publish terms (client names, PII, private identifiers) intentionally live *outside* this public repo in a private local file — publishing the denylist would defeat it.

```bash
#!/usr/bin/env bash
# scan gate — all checks must pass before any tag push
set -u
cd "$(git rev-parse --show-toplevel)"
FAIL=0

# 1. Never-publish terms from the private denylist (not in this repo, by design)
DENYLIST="$HOME/.clearbox/never-publish.txt"
if [ -f "$DENYLIST" ]; then
  while IFS= read -r term; do
    case "$term" in ''|'#'*) continue;; esac
    if grep -riqE "$term" . --exclude-dir=.git --exclude-dir=__pycache__; then
      echo "FAIL: denylist term matched: $term"
      grep -rilE "$term" . --exclude-dir=.git --exclude-dir=__pycache__; FAIL=1
    fi
  done < "$DENYLIST"
else
  echo "FAIL: private denylist not found at $DENYLIST — cannot release without it"; FAIL=1
fi

# 2. Second denylist: shawn-gtme-os blocklist, if present on this machine
BLOCKLIST="$HOME/shawn-gtme-os/.claude/blocklist.txt"
if [ -f "$BLOCKLIST" ]; then
  while IFS= read -r term; do
    case "$term" in ''|'#'*) continue;; esac
    if grep -riqE "$term" . --exclude-dir=.git --exclude-dir=__pycache__; then
      echo "FAIL: blocklist term matched: $term"; FAIL=1
    fi
  done < "$BLOCKLIST"
fi

# 3. Local infra: absolute home paths, and env-file references
# (bracketed patterns so this file does not match itself; .env.notion is the
# push tool's own documented config convention and is allowed)
grep -rnE '/U[s]ers/' . --exclude-dir=.git --exclude-dir=__pycache__ \
  && { echo "FAIL: absolute home path leak"; FAIL=1; }
grep -rnE '\.e[n]v\.' . --exclude-dir=.git --exclude-dir=__pycache__ --exclude=.gitignore \
  | grep -v '\.env\.notion' && { echo "FAIL: env-file reference leak"; FAIL=1; }

# 4. Private identifiers: org tokens
grep -rnE 'org_[A-Za-z0-9]{20,}' . --exclude-dir=.git --exclude-dir=__pycache__ \
  && { echo "FAIL: private org id"; FAIL=1; }

# 5. Language rule: the views claim is "1.5M+", never the next million up
grep -rniE '2[m]\+|2 milli[o]n' . --exclude-dir=.git --exclude-dir=__pycache__ \
  && { echo "FAIL: forbidden views claim"; FAIL=1; }
grep -q '1\.5M+' proof/README.md || { echo "FAIL: proof/README.md missing 1.5M+ claim"; FAIL=1; }

# 6. PARTNERS.md stays number-free (no percentages, dollars, durations)
[ -f PARTNERS.md ] && grep -nE '[0-9]+ ?%|\$[0-9]|[0-9]+ ?(month|mo)\b' PARTNERS.md \
  && { echo "FAIL: numbers in PARTNERS.md"; FAIL=1; }

# 7. Transparency docs teach lessons, never evasion
[ -d transparency ] && grep -rniE 'bypass|evade|get past|circumvent|slip (past|through)' transparency/ \
  && { echo "FAIL: evasion language in transparency/"; FAIL=1; }

# 7B. Client-facing agency guidance excludes admin and internal implementation detail
grep -rniE 'Stripe customer|billing is independent|Freckle workbook|Base Loop workspace|workspace [a-z0-9]{20,}|field [a-z0-9]{20,}|runs? [a-z0-9]{20,}' \
  skills/reddit-agency README.md \
  && { echo "FAIL: admin or internal implementation detail in client-facing agency guidance"; FAIL=1; }

# 8. Python compiles
python3 -m compileall -q engine proof scripts || { echo "FAIL: compileall"; FAIL=1; }

# 9. Proof pipeline is fresh and idempotent (run it, then require zero diff)
python3 proof/generate_proof.py --with-logpose || { echo "FAIL: proof generator"; FAIL=1; }
git diff --exit-code proof/ || { echo "FAIL: proof output not committed"; FAIL=1; }

# 10. Relative links in playbooks resolve
for f in playbooks/*.md; do
  grep -oE '\]\((\.\.?/[^)#]+)' "$f" | sed 's/^](//' | while IFS= read -r link; do
    target="$(dirname "$f")/$link"
    [ -e "$target" ] || { echo "FAIL: dead link in $f -> $link"; exit 9; }
  done || FAIL=1
done

# 11. Public URLs referenced by the docs respond
for url in https://clearbox.to https://shawnos.ai/reddit https://shawnos.ai/vault \
           https://github.com/shawnla90/gtm-coding-agent; do
  code=$(curl -sL -o /dev/null -w '%{http_code}' "$url")
  [ "$code" = "200" ] || { echo "FAIL: $url returned $code"; FAIL=1; }
done

[ "$FAIL" = 0 ] && echo "SCAN GATE: all green" || echo "SCAN GATE: FAILED"
exit "$FAIL"
```

## Release checklist

1. Proof stats fresh (`asOf` within 14 days) — re-run the generator if not.
2. Scan gate above: all green.
3. `CHANGELOG.md` top block written for the new version.
4. Push `main`, then tag the pushed commit, then `git rev-parse 'vX.Y.Z^{commit}'` must equal `origin/main`.
5. Release notes = the top changelog block (see `RELEASING.md`).
6. If CI already drafted the release, publish that draft — don't create a second.
