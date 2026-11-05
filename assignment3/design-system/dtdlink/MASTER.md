# DTDLINK interface design system

Updated 5 November 2026. User-authorised redesign of the existing local React
application, using UI UX Pro Max as design guidance. The later explanation update
extends the offline API presentation layer; the A2 model remains unchanged.

## Source and use

- Next Level Builder, *UI UX Pro Max*, MIT licence.
- Repository: https://github.com/nextlevelbuilder/ui-ux-pro-max-skill
- Reviewed revision: `b7d5353e0130feb8c5574ef1251f8a1db1873ccb`.
- Read `.claude/skills/ui-ux-pro-max/SKILL.md` and the web quick reference.
- Ran the repository's standard-library Python search script locally:

```sh
python search.py 'cybersecurity AI tool dark minimal' --design-system -p DTDLINK --variance 6 --motion 2 --density 4 --format markdown
python search.py 'AI-Native UI' --domain style -n 1
python search.py 'dark mode OLED' --domain style -n 1
python search.py 'dark theme accessible forms' --stack react -n 3
```

Relevant recommendations: minimal chrome, prominent input, contextual result
cards, one accent colour, semantic tokens, SVG icons, visible focus, sufficient
contrast, responsive layout and reduced-motion support. The default generated
light palette and video-led landing-page pattern were rejected after review:
DTDLINK is a task-focused URL tool, so this implementation uses a dark workspace.
Recommendations were adapted to the installed React/plain-CSS stack. No Tailwind,
chatbot, streaming response, online AI service or new runtime dependency added.
The third-party Python search tool is a design-time aid, not an app dependency.

## Direction

Graphite canvas, violet accent, centred shield mark and headline, a spacious URL
composer, compact navigation, quiet borders, and contextual evidence cards.
Static CSS/SVG decoration; no continuous background animation. Form feedback and
result states remain explicit. Only the existing loading indicator rotates.

The app remains a local Random Forest classifier. The input caption identifies
Random Forest and 36 features. Label, uncalibrated confidence, real host,
rule-based signals and limitations retain their existing meaning. Do not add
fake conversational output or historical dataset statistics.

## Implementation rules

- Tokens: `frontend/src/styles.css` `:root`; components use semantic variables.
- Surfaces: background, sidebar, surface, surface-raised, surface-inset.
- Text: foreground, muted, subtle; purple accent; separate danger/success/warning.
- Chart fills, axes, labels and tooltip surfaces use the same tokens.
- Typography: existing offline system stack (Inter when installed, then native
  system sans-serif); no font downloads or remote imports at runtime.
- Type hierarchy: headline 34–50px, section 19–22px, prose 12–16px, compact
  supporting labels 9–12px. URL input remains 16px on phones.
- Controls have a 44px minimum height; clear/menu controls are 44px square.
- Borders rather than excessive glow distinguish surfaces. Primary buttons use
  white text on violet; hover darkens the fill to preserve text contrast.
- Visible keyboard focus; labels, error association, loading/disabled states,
  Enter submission and live announcements remain in place.
- Dark native selects via `color-scheme: dark`; navigation becomes a drawer
  below 760px. Grid cards stack on narrow screens. Respect reduced motion.
- Submitted URLs remain escaped, non-clickable text. Preserve CSP and local-only
  API traffic; do not introduce externally loaded icons, fonts or scripts.

## Verification

See `evidence/ui-redesign-verification.json` for executed checks, measured CSS
widths, screenshot paths, unchanged backend checksums and limitations. These
checks are a bounded UI review, not a full accessibility certification.

## Detailed analysis update

The user requested clearer, more specific URL analysis. Keep the actual host
prominent, highlight the exact host/userinfo boundaries, and use a native details
control for the full URL breakdown. Observation cards use evidence, meaning and
next-step columns, stacked on phones; show three by priority before offering
more. Never invent a model rationale or imply verified website ownership.

The targeted skill searches for progressive disclosure returned unrelated heading
layout guidance, including the one narrower retry. That result was discarded;
this interaction follows the skill's general forms/accessibility checklist and
the existing local design tokens, rather than a claimed database match.
