# Automated promotion: one daily Bluesky post

This repository-ready folder contains a 30-day campaign for the $5 Job Offer Reality Check calculator. It posts to **your own Bluesky account**, with a clickable Payhip product link. It does not send DMs or replies.

## One-time connection

Use a free Bluesky-hosted account and a free GitHub account. When GitHub is connected in ChatGPT, ask the agent to publish this folder as a new public repository and configure the non-secret variables. Enter the App Password yourself in GitHub Secrets; never put it in a repository file or send it in chat.

If you do it from iPhone Safari:

1. Create a **public** GitHub repository named `job-offer-promotion`. Initialize it with a README. Do not upload the paid workbook, customer ZIP or seller kit to this repository.
2. Upload `post.py`, `posts.json` and `test_post.py` to the repository root. Add the contents of `.github/workflows/promote.yml` at that exact repository path. For iPhone file pickers that hide dotfolders, open the supplied `Workflow-To-Paste.txt`, copy it, and use GitHub's Add file > Create new file with `.github/workflows/promote.yml` as the name. Safari's Request Desktop Website may help.
3. In the Bluesky app, find App Passwords in Settings (usually under Privacy and Security or Advanced). Create a dedicated password named `Job offer promotion`. Do not enable direct-message access. The code supports Bluesky-hosted accounts, not custom self-hosted servers.
4. In GitHub repository Settings > Secrets and variables > Actions > Secrets, add:
   - `BSKY_HANDLE`: your full handle, such as `name.bsky.social`.
   - `BSKY_APP_PASSWORD`: the dedicated Bluesky App Password.
5. Under Variables, add:
   - `PRODUCT_URL`: your published product link, e.g. `https://payhip.com/b/Ab123`.
   - `CAMPAIGN_START_DATE`: the UTC date when the campaign should begin, formatted `YYYY-MM-DD`.
   - `PROMOTION_ENABLED`: `false` initially.
6. Read `posts.json`. Confirm the product is published at $5 and the link is correct. In Actions > Daily product promotion > Run workflow, leave Preview checked. Inspect the resulting post in the run log. Preview does not authenticate or post.
7. Change `PROMOTION_ENABLED` to `true`. Run the workflow again with Preview unchecked to publish today's post, or wait for the scheduled run. Check the post on your account and test its link once. Retry runs will not create a second post for the same campaign day.

## What runs

GitHub runs the workflow at about 18:17 UTC daily (11:17 a.m. Pacific daylight time / 10:17 a.m. Pacific standard time). Scheduled workflows can be delayed or dropped; exact timing is not guaranteed. Scheduling runs from the default branch. The day number comes from UTC date minus the campaign start date. Before the start date and after day 30, it posts nothing. Missed calendar days are not caught up automatically.

The runner is standard `ubuntu-latest`, with a three-minute timeout and read-only repository permissions. No packages, AI API, paid advertising, artifact storage or caches are used. Standard runners for public repositories are currently free. GitHub can disable public scheduled workflows after 60 days without repository activity; the supplied 30-day campaign ends first. Extending a campaign may require re-enabling its workflow.

## Stop or extend

Set `PROMOTION_ENABLED=false` or disable the workflow to stop. Revoke the Bluesky App Password to remove access. These actions do not remove existing public posts.

For more promotion, add new distinct posts to `posts.json`, keeping each final post under 300 characters including the link. The code stops when it reaches the end of this list. Avoid recycling the same sales message indefinitely. Starting over with a new start date creates a new campaign; keep that intentional.

## Verify

`python3 -m unittest -v test_post.py`

Tests are local and use fake API responses. To complete the live test, publish one post from your authenticated account, check it on Bluesky and click the product link. GitHub's failure notification settings control whether you receive email about failed runs. Automated reach and sales are not guaranteed, especially on a new account with no audience.
