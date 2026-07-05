# linkedin-autopost

Daily automated LinkedIn posts about iOS / Swift / SwiftUI,
generated and published by a Claude Code Routine.

## Contents
- `make_card.py` — renders the branded 1200x1200 code card (PNG).
  The routine edits only: TIP_NO, HEADLINE, FILENAME, CODE.
- `fonts/` — JetBrains Mono + Inter, required by the script.
- `posted_topics.md` — history log so topics never repeat.

## Environment (set in claude.ai Settings → Environments)
- Env var: `LINKEDIN_ACCESS_TOKEN`
- Network access: allow `api.linkedin.com`
- Setup script: `pip install pillow requests --break-system-packages`

## Notes
- Script expects fonts in `./fonts` relative to repo root (FONT_DIR).
- LinkedIn token expires every ~60 days; the routine reports a clear
  message on HTTP 401 instead of retrying.
# linkedin-autopost
