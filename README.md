# Automated promotion for the Student Pay and Commute Calculator

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
