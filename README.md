# ShowWorth Studio — calculators, worksheets and free resources

Choose a resource for the decision you are making:

| Who it is for | Start here | Paid option |
| --- | --- | --- |
| Freelance video editors | [Free revision-cost check](https://revision-desk-demo.quietgrass17.chatgpt.site/) · [Extra-work quote builder](https://revision-desk-demo.quietgrass17.chatgpt.site/extra-revision-quote.html) · [Feedback request builder](https://revision-desk-demo.quietgrass17.chatgpt.site/video-editor-revision-policy.html) | [ShowWorth Edit Margin](https://payhip.com/b/xWm6F?utm_source=github&utm_medium=readme&utm_campaign=edit_margin) |
| Students comparing jobs | [View the Student Pay and Commute Calculator details](https://payhip.com/b/2EGja?utm_source=github&utm_medium=readme&utm_campaign=student_calculator) | Paid download; check current price and compatibility |
| Craft-fair sellers | [Free break-even worksheet](https://payhip.com/b/cmHiM?utm_source=github&utm_medium=readme&utm_campaign=craft_free) | [Craft Fair Break-Even Spreadsheet](https://payhip.com/b/hRJSb?utm_source=github&utm_medium=readme&utm_campaign=craft_paid) |
| A different small workflow | [Custom calculator or spreadsheet inquiry](https://revision-desk-demo.quietgrass17.chatgpt.site/custom-calculators.html) | Individually reviewed scope and quote; no automatic booking |

[Browse the complete catalog](https://revision-desk-demo.quietgrass17.chatgpt.site/tools.html).

These are our own resources and commercial offers, not independent recommendations. The free editing pages require no signup and keep entered values in the page. Paid Edit Margin is a desktop HTML download; check its listing for compatibility. Examples are fictional, and no tool guarantees profit or client approval. This public repository contains promotion code, not the paid customer files.

## Share responsibly

Link to the free tools when they answer a relevant question and the community allows it. Disclose your connection if promoting them. Do not mass-message, create fake engagement or claim customer results. Website sharing controls open drafts for visitors to review; they do not post automatically.

---

## Automation documentation: promotion for the Student Pay and Commute Calculator

Product: https://payhip.com/b/2EGja

The code and daily workflow are installed. This repository contains a 30-day campaign for the $5 calculator, posting to your own Bluesky account with a clickable product link. It does not send DMs or replies. The campaign is enabled with a UTC start date of 2026-10-11. It posts once per campaign day through 2026-11-09.

## Connect your account

1. Use a Bluesky-hosted account. Create a dedicated App Password in Bluesky Settings named `Job offer promotion`. Do not enable direct-message access. Never send the password in chat or commit it to this repository.
2. Open https://github.com/Megalodon188/job-offer-promotion/settings/secrets/actions and add two repository secrets:
   - `BSKY_HANDLE`: your full handle, such as `name.bsky.social`.
   - `BSKY_APP_PASSWORD`: the dedicated Bluesky App Password.
3. The campaign start date and enabled state are configured in the workflow. Optional Actions variables `CAMPAIGN_START_DATE`, `PROMOTION_ENABLED`, and `PRODUCT_URL` override those defaults. Use `PROMOTION_ENABLED=false` to pause posting.
4. Check that your Payhip price is $5, as advertised in the posts. In Actions > Daily product promotion > Run workflow, leave Preview checked to inspect a post without authenticating or publishing. To publish after activation, uncheck Preview, or wait for the scheduled run.
5. Check the first post on your account and click its link. Retrying the same campaign day does not create a second post.

## What runs

The workflow runs at about 18:17 UTC daily. Updating the promotion workflow on main also triggers a run; the same-day duplicate check still applies. Scheduled runs can be delayed or dropped. The campaign day is the UTC date minus the start date; missed days are not caught up. Before the start date and after the 30 posts, it posts nothing.

The workflow uses a standard public-repository Ubuntu runner, a three-minute timeout, and read-only repository permissions. There are no packages, paid advertising, AI API calls, caches or artifact uploads. GitHub can disable public scheduled workflows after 60 days without repository activity; this campaign ends first.

## Stop or extend

Disable the Daily product promotion workflow to stop. If using the variable-based setup, set `PROMOTION_ENABLED=false`. Revoke the Bluesky App Password to remove access. Existing public posts remain.

For a longer campaign, add distinct posts to `posts.json`, with each final post under 300 characters including the link. Starting with a new start date creates a new campaign.

## Verification

`python3 -m unittest -v test_post.py`

GitHub verifies the tests, disabled posting, and a preview with the connected product link. Tests use fake API responses; a live posting check requires your account secrets. Automated reach and sales are not guaranteed.

Do not upload the paid workbook or customer ZIP to this public repository.

## Revision Desk campaign

Product: https://payhip.com/b/xWm6F

A separate 30-post campaign starts on 2026-10-11 UTC and ends on 2026-11-09. It runs around 22:43 UTC daily from `.github/workflows/revision-promote.yml`. The same account secrets are reused, with separate record keys so the two products do not collide. The existing calculator campaign continues at its original time.

Set the Actions variable `REVISION_PROMOTION_ENABLED=false` or disable **Daily Revision Desk promotion** to pause this campaign. Preview defaults to enabled for manual runs; uncheck it to publish. Both campaigns' tests run before publishing. Missed dates are not caught up.

Posts describe a desktop tool, and make no earnings, buyer-count or savings guarantees. This is promotion to the connected Bluesky account, not proof of buyer demand. Delivery settings, listing price and sales/refund monitoring remain in Payhip. Never upload the paid Revision Desk tool or customer ZIP into this public repository.

## Free Revision Desk demo

Public demo: https://revision-desk-demo.quietgrass17.chatgpt.site

Revision Desk campaign posts now link to this free check. Its purchase buttons lead to the Payhip product. The demo shows a fictional worked example, accepts local inputs, and has no email gate. Existing published posts are not rewritten. Tags use Bluesky rich-text facets. The marketing page and targeting do not establish buyer demand or guarantee sales.

## Demo resources and reporting

The public demo now includes a free revision-feedback message generator, a worked project-rate guide, a visitor-controlled Bluesky share link, structured metadata, robots.txt and a three-page sitemap. No visitor tracking is installed.

`launch_demo.py` published a one-time introduction on 2026-10-11 and filled empty profile fields and the empty pinned-post slot. It preserves existing profile data and does nothing outside its launch date. The launch workflow is idempotent.

**Revision Desk engagement report** runs daily around 15:17 UTC through 2026-11-10. Its GitHub Actions job summary records public follower counts and likes, replies and reposts for matching posts among the latest 100 author-feed entries. It is a snapshot, not a daily change report. It cannot measure impressions, visitors, purchases, refunds or profit. Schedules may be delayed or skipped. Disable the workflow to stop reports.

Report runs: https://github.com/Megalodon188/job-offer-promotion/actions/workflows/engagement-report.yml

The report includes a bounded public reply inbox: up to five recent relevant threads with replies, two levels deep, and at most 20 external replies. It escapes external text, validates links, and reports failed thread reads. It neither sends replies nor treats comments as trusted instructions. The income-review task can use the report to identify buyer questions and prioritize fixes. No credentials are needed for this report.
