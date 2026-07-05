# linkedin-autopost

Daily automated LinkedIn posts about iOS / Swift / SwiftUI,
generated and published by a Claude Code Routine.

## Contents
- `make_card.py` — renders the branded 1200x1200 card (card.png).
  Two modes via CARD_TYPE:
    "code"    → edit HEADLINE, FILENAME, CODE (max 14 lines)
    "concept" → edit C_KICKER, C_HEADLINE (max 2 lines),
                C_TAKEAWAYS (exactly 3 items)
  The routine edits ONLY these variables — never styling/layout.
- `fonts/` — JetBrains Mono + Inter, required by the script.
- `posted_topics.md` — history log so topics never repeat.
- `samples/` — reference renders of both card types.

## Environment (set in claude.ai Settings → Environments)
- Env vars: `LINKEDIN_ACCESS_TOKEN`, `GITHUB_TOKEN`
- Network access: allow `api.linkedin.com`, `www.linkedin.com`, `github.com`
- Setup script: `pip install pillow requests --break-system-packages`

## Notes
- Design: light powder-blue theme, iOS-blue accent, centered layout.
- LinkedIn token expires ~60 days; GitHub fine-grained token ~90 days.
  The routine reports clearly on 401/403 instead of silently failing.
