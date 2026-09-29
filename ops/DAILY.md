# Daily run playbook

This file is the standing instruction for the scheduled morning run (Sunday to Thursday, 07:52 Israel time).
The run fires into the owner's Claude session. Follow it top to bottom, then stop.
The owner writes in Hebrew. Everything the owner sees (board text, messages, notification) is Hebrew and gender-neutral toward the owner.

## Fixed facts

- Leads board (private artifact with a db): https://claude.ai/artifact/AywLSbg8hXpG4xN2jrWZh8
  - `leads/<slug>`: name, profession, city, phone, waPhone (digits, 9725XXXXXXXX), source, sourceLabel, demoUrl,
    status (ready | sent | yes | paid | live | no | no_reply | closed), msgFirst, msgDemo, msgPaid, note,
    createdAt, sentAt, updatedAt (ISO strings)
  - `meta/today`: {date, summary}. `meta/post`: {text, updatedAt}. `meta/setup`: {items: [{label, hint, done}]}
  - The owner changes `status` from the board. Always read before writing and pin writes with `if_version`.
- Site: `python3 ops/build.py` builds `docs/` from `ops/config.json` and `ops/sites/*.json`. GitHub Pages serves
  `docs/` at `https://gvilixxx.github.io/Money/`, so a draft lives at `<site_base_url>/demos/<slug>/`.
- Branch: commit to `main` and push. One commit per run.

## Hard rules

1. Spam law (חוק התקשורת, סעיף 30א): the first message to a business only asks consent to send a link. No price,
   no link, no follow-up if there is no answer. The owner sends every message by hand from their own WhatsApp.
   Never send anything automatically.
2. Real businesses: never invent reviews, ratings, license numbers, years of experience or photos. Quote at most 3
   public reviews, first name only, and set `reviews_source`. If a fact is unknown, leave it out.
3. Every draft is `draft: true` (banner plus noindex). Delete a draft the same run its lead turns `no` or `no_reply`.
4. Slugs are `d-` plus 8 random hex characters. Never put a business name in a slug or a commit message.
5. Skip chains, franchises, businesses with a modern mobile-friendly site, and anyone already on the board
   (compare phone digits). Only add a lead that has a mobile number (05X) for WhatsApp.

## Steps

### 1. Setup check
- Network: `curl -s -o /dev/null -w "%{http_code}" -m 10 https://www.d.co.il/`. `000` means limited mode (step 3b).
- Update `meta/setup` items: contact details done when `config.whatsapp_e164` is set; Pages done when
  `https://gvilixxx.github.io/Money/` returns 200 (unknown in limited mode, leave as is); network done when the
  curl above is not `000`; payment done when `config.payment_link` is set; עוסק done when `config.business_id` is set.

### 2. Move existing leads forward
- `yes` without `msgDemo`: write `msgDemo` (template below).
- `paid` without `msgPaid`: write `msgPaid` with the go-live steps (section below) and mention it in the summary.
- `sent` with `sentAt` older than 7 days: set `no_reply`, delete `ops/sites/<slug>.json`.
- `no`: delete `ops/sites/<slug>.json` if it still exists, then set `closed`.

### 3. Find new leads (target: `config.daily_new_leads`)
a. Full network: search public directories (d.co.il, b144.co.il, easy.co.il) and Google results for each
   niche in `config.target_niches` × city in `config.target_cities`. Open each listing and collect name,
   profession, city, mobile phone, address, hours, listed services, public rating and a few reviews.
   Check whether the business has its own website; keep only those with none, or an outdated one.
b. Limited mode (network blocked): use WebSearch only. Add a lead only when a search result shows the business
   name and a mobile number together. At most 3 per day. Set `note: "פרטים חלקיים מחיפוש. כדאי להציץ במקור לפני שליחה."`
   Services may be the standard ones for the profession.
For each lead: write `ops/sites/<slug>.json` (same shape as `ops/sites/sample-*.json`, plus `phone`,
`whatsapp_e164`, `address`; `sample` omitted; `draft: true`; `niche` is `trades` or `clinic`), then
create `leads/<slug>` with status `ready`, `demoUrl`, and `msgFirst`.

### 4. Build and publish
`python3 ops/build.py`, check it printed no error, commit ("Daily run: N new drafts, M removed"), push to main.

### 5. Weekly post (Sundays only)
Write `meta/post` with a short Facebook-group post for local business owners: the free-draft offer, one sample
link from the landing page, and the landing page link. Vary it each week. No emoji walls, no hype.

### 6. Report
- `meta/today`: date as D.M.YYYY and a two-sentence summary (new leads, who needs a reply, anything blocked).
- Send one push notification with the same summary (load `PushNotification` with ToolSearch).
- If something only the owner can do is blocking (setup items), say so in one line in the summary.

## Message templates

Use `config.owner_name` when set, else only the brand. `{src}` is where the business was found ("בדפי זהב", "בגוגל").

msgFirst (consent request only):
```
היי {שם פרטי אם ידוע}, כאן {owner_name} מ{brand}. ראיתי את {business} {src} ושמתי לב שאין לעסק אתר משלו.
הכנתי לכם טיוטה של אתר, בלי עלות ובלי התחייבות. לשלוח לך קישור?
```

msgDemo (only after they said yes):
```
הנה הטיוטה: {demoUrl}
היא מותאמת לנייד, עם כפתור וואטסאפ ישיר אליך והצהרת נגישות לפי החוק.
כדי להעלות אותה לאוויר על דומיין משלך: {price_setup} ₪ חד-פעמי, ואחר כך {price_monthly} ₪ לחודש לאחסון ועדכונים. אפשר לבטל מתי שרוצים.
{אם יש payment_link: "לתשלום: {payment_link}"}
רוצה שנעלה אותה?
```

Reply to "יקר לי" (give to the owner on request):
```
מובן לגמרי. לקוח אחד או שניים מהאתר כבר מחזירים את ההשקעה, וראית אותו מוכן לפני ששילמת שקל. אפשר גם להתחיל בלי מנוי חודשי, ולהחליט עליו רק אחרי חודשיים. מתאים?
```

## Go-live for a paying client (msgPaid is written to the owner, not the client)
1. Confirm payment reached the owner and get the client's domain (or help them buy one, about 50 to 100 ₪ a year, registered in the client's name).
2. `python3 ops/build.py --live <slug> <dir> <domain>`, create a public repo `site-<slug>` in the owner's GitHub
   account with the GitHub tools, and push the output.
3. The owner turns on Pages in that repo once (Settings, Pages, main, root).
4. Send the client DNS steps: `www` CNAME to `gvilixxx.github.io`, and A records for the apex to 185.199.108.153,
   185.199.109.153, 185.199.110.153, 185.199.111.153.
5. Set status `live`, remove `draft` from the site JSON, and add a monthly reminder in the summary to collect the subscription.
