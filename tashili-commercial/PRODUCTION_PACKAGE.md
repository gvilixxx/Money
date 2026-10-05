# TASHILI — "לצאת מהארון" (60s, 16:9, 1920×1080+)

**Status: NOT produced.** This is the hand-off package. No video, audio or logo asset exists yet. See "Blockers" below.

## Blockers found in this environment (2026-10-05)

| Needed | State |
|---|---|
| Original logo file | **Missing.** `/mnt/attach`, `/mnt/user-data/uploads` and the repo are empty. The brief forbids redrawing the wordmark, so none was made. |
| Photoreal live-action footage (owner, renter, party, desert, backyard) | No video or image generation model reachable. Only ffmpeg is installed. |
| Hebrew voice performance (5 voices) | No Hebrew TTS installed. Hosted TTS (Edge) and Hugging Face are blocked by the egress proxy. Only PyPI is reachable. |
| Hebrew font | No Hebrew-capable sans-serif besides FreeSans/DejaVu. A proper font (e.g. Heebo, Assistant, Rubik) must be supplied. |
| Real app screenshots | None supplied. Conceptual UI only (see 00:20). |
| Music / sonic logo | Nothing licensed or composed. |

Needed to unblock: the logo (SVG/PNG, preferably transparent or white background), a Hebrew-capable video+voice generation route or a studio, and a font file.

## Timeline, dialogue and sound (dialogue verbatim from the brief)

| Time | Picture | Hebrew | Sound |
|---|---|---|---|
| 00:00–00:03 | Original logo, centered on white, frame 1. Hard cut to dark closet interior; door opens on the next beat. | Speaker (muffled, from the closet): **סליחה… מישהו מוציא אותי מפה?** | Sonic logo in the first ~0.5s, then room tone. Closet door. |
| 00:03–00:13 | Shot 1: black speaker, shopping bag on top. Shot 2: olive tent beside stacked bed linen. Shot 3: light projector in a drawer. | Speaker: **פעם הרמתי מאתיים איש. היום אני מחזיק שקית.** Tent: **כתוב עליי ״אקסטרים״. אני ליד המצעים.** Projector: **יש בי סרט שלם… והוא רואה בטלפון.** | Near silence, room ambience, fabric, bag rustle. A beat of air after each joke. |
| 00:13–00:20 | Owner with mug, confused. Cut to speaker, cut to tent, back to owner looking at his coffee. | Owner: **מה אתם רוצים ממני?** Speaker: **לצאת. לפגוש אנשים. לעבוד קצת.** Tent: **אתה יכול להישאר.** | Mug set down, closet room tone. |
| 00:20–00:26 | Owner opens the app, photographs the speaker, creates a listing. Turquoise arrow from his listing to a second phone. | VO: **מה שיושב אצלכם בלי שימוש, יכול להיות בדיוק מה שמישהו אחר צריך.** | Phone taps; light rhythmic build begins. |
| 00:26–00:40 | Three rentals, each with a human handover then a match cut: (1) woman browses and coordinates, handover, match cut to rooftop party at sunset; (2) tent handed to a couple, match cut to desert campsite in morning light; (3) projector on a backyard table, switch-on, outdoor movie night with original/abstract projected footage. | VO: **ב־תשאיל לי מעלים מוצרים להשכרה, מוצאים דברים שצריכים ומתאמים ישירות עם מי שמשכיר. לאירוע, לסוף שבוע, או לפרויקט הבא.** Captions, one at a time: **מפרסמים להשכרה** → **מוצאים מה שצריך** → **מתאמים ביניכם** | Full groove. **First strong bass hit lands exactly when the rooftop speaker starts.** Handover foley, tent unzip, projector switch. |
| 00:40–00:49 | Split screen. Right: owner hands speaker to renter. Left: renter sets it down at her party, friends dance. Speaker position/movement merges both halves into one full-screen party shot. No payment or earnings UI. | VO: **צריכים משהו לזמן קצר? שוכרים. יש לכם משהו שאחרים צריכים? מציעים להשכרה ומרוויחים מהשימוש בו.** | Groove at full energy; VO above it. |
| 00:49–00:55 | Evening, owner's apartment; same speaker returned. Owner beside it. Reaction beat. Owner switches off the room light. | Owner: **נו, איך היה?** Speaker (slightly hoarse): **אל תשאל. תשאיל.** | Music ducks for the joke. Light-switch click lands on a musical accent. |
| 00:55–01:00 | Clean white end card, original logo large and centered. Optional turquoise/blue accent arrows that do not touch the logo artwork. Tagline **משכירים ושוכרים. בין אנשים.** CTA **גלו את TASHILI**. Hold the full card ≥2s. No fade to black. | VO: **תשאיל לי. יש לכם מה להציע. יש למישהו מה לעשות עם זה.** | Music resolves into the sonic logo. |

## Timing risks to check at the first VO recording

Syllable counts are my estimates. Natural Israeli delivery is roughly 4–5 syllables per second.

- **00:00–00:03** is the tightest. The 11-syllable line plus the sonic logo leaves about 2.5s. Keep the sting short or start the line at about 0.6s.
- **00:20–00:26**: about 22 syllables, about 4.5–5s of speech. It fits, but the app sequence must be cut to the VO.
- **00:40–00:49**: about 38 syllables, about 8s of speech in a 9s window. There is almost no slack, so don't slow the read.
- **00:55–01:00**: the VO is about 4s. The end card must be fully built by 00:58 to hold the required 2s.
- Key dialogue never overlaps narration. The only dialogue-then-VO handoffs are at 00:20 and 00:49.

## Post-production specs

- Hebrew overlays are built in post, never painted into generated frames. Font: Heebo, Assistant or Rubik, Bold. RTL base direction.
- Mixed line "גלו את TASHILI": set the paragraph direction to RTL and wrap the Latin run in an LTR isolate (U+2066 … U+2069). Verify it visually.
- The logo is placed as the supplied file: uniform scale only, no crop, no recolor, on pure white. If the logo's arrows can't be separated, keep the logo static and animate separate accent arrows in its navy, turquoise and blue.
- Safe margins: 5% of frame width and height. Caption cap height at least 5% of frame height so it reads on a phone.
- Continuity bible: the same owner (Israeli man, early 30s, neutral casual clothing), the same apartment, the same black portable speaker, the same olive tent with its matching bag, and the same compact light projector. Reuse reference frames across all shots.
- No cartoon eyes, mouths or limbs. The objects "speak" through voice and cutting only.
- No invented features: no insurance, verification, delivery, payments, earnings figures or app-store badges.

## Per-shot generation notes (for a video model or a shoot)

1. **Closet** — dark, dusty, handheld-still. Black speaker under a paper shopping bag, shallow depth of field. Door opens to soft window light.
2. **Tent** — folded olive tent and its bag on a shelf next to ironed white linen. Slow push-in.
3. **Projector** — light-colored compact projector in a half-open drawer among cables. Slow rack focus.
4. **Owner** — medium shot, mug in hand, eyebrows up, not scared. Muted beige/grey grade for the whole apartment.
5. **Handovers** — front doorway, two real hands passing the object. Hold the handover for one full second before each match cut.
6. **Rooftop** — golden hour, friends dancing, the same speaker in the foreground, with the speaker's position fixed to the match cut frame.
7. **Desert camp** — morning light, tent being unfolded by a couple, light breeze on the fabric.
8. **Backyard** — string lights, table, projector beam onto a sheet, abstract/original abstract footage only.
9. **Split screen** — hard vertical divider on the center line. The speaker crosses the divider as a wipe into the party shot.
10. **Return** — evening apartment, the same speaker on the same shelf, one clear establishing frame before the owner enters.

## QC checklist (run before export)

Runtime exactly 60.000s · 16:9, ≥1920×1080 · logo on frame 1 and the last frame · all dialogue and copy in Hebrew except the logo lettering · RTL and spelling correct · each line fits its window without rushing · same people and objects throughout · speaker visibly returned · no unsupported features or financial claims · phone screens, hands and faces clean · "אל תשאל. תשאיל." clearly audible · end card stable for at least the final 2s.
