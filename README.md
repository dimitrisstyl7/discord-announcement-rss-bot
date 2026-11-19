# Discord RSS Announcement Bot

## Description

This bot fetches announcements from a university's eClass announcements section (via RSS) and posts them in a Discord
channel using webhooks.

The current implementation in `announcements-bot.py`, specifically the function [
`fetch_announcements`](app/announcements-bot.py),
is tailored to handle the data structure of
the [RSS feed](https://thales.cs.unipi.gr/modules/announcements/rss.php?c=TMG118) of the
[eClass system](https://thales.cs.unipi.gr/modules/announcements/?course=TMG118) used by the _University of Piraeus -
Department of Informatics_.

To use the script with other RSS-supported websites, you will need to modify the logic in [
`fetch_announcements`](app/announcements-bot.py)
to match the RSS feed structure of the target website.

## Features

- Fetches announcements automatically from the university eClass RSS feed.
- Posts them directly to Discord via webhooks.
- Provides easy configuration and customization for your specific RSS feed and Discord server.

## GitHub Actions

The workflow checks every hour, Monday through Friday, from 08:00 to 20:00 inclusive in `Europe/Athens`. GitHub handles
daylight saving time. Scheduled runs can be delayed or dropped, and the bot checks only the latest five feed entries.

### Setup

1. In your repository, open **Settings > Secrets and variables > Actions > New repository secret**. Add:
    - `ANNOUNCEMENTS_WEBHOOK_URL`: Discord webhook for announcements.
    - `ERRORS_WEBHOOK_URL`: Discord webhook for error notifications.
    - `RSS_URL`: eClass RSS feed URL.
2. Copy the existing `last_announcement_id.txt` value into `state/last_announcement_id.txt` in this branch. If there is
   no existing checkpoint, `-1` sends up to the latest five announcements.
3. Under **Settings > Actions > General > Workflow permissions**, allow read and write permissions. The default branch
   must also allow the workflow's `GITHUB_TOKEN` to push checkpoint commits; branch protection or rulesets may block
   this.
4. Stop the existing bot to avoid duplicate posts. Commit and push these changes, then merge the branch into the default
   branch. Scheduled workflows run only from the default branch.
5. Open **Actions > Announcements > Run workflow**, select the default branch, and run it. Check the run's logs and
   Discord. If there are no new announcements, no Discord message is expected.

The workflow commits `state/last_announcement_id.txt` to the default branch after messages are sent. A failed checkpoint
push or an interrupted run can cause duplicates; check failed runs under **Actions**. If a webhook fails, successfully
sent announcements are checkpointed and the failed announcement is retried on the next run.

## Contributors

<table>
  <tr>
    <td align="center"><a href="https://github.com/thkox"><img src="https://avatars.githubusercontent.com/u/79880468?v=4" width="100px;" alt="Theodoros Koxanoglou"/><br /><sub><b>Theodoros Koxanoglou</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/ApostolisSiampanis"><img src="https://avatars.githubusercontent.com/u/75365398?v=4" width="100px;" alt="Apostolis Siampanis"/><br /><sub><b>Apostolis Siampanis</b></sub></a><br /></td>
    <td align="center"><a href="https://github.com/dimitrisstyl7"><img src="https://avatars.githubusercontent.com/u/75742419?v=4" width="100px;" alt="Dimitris Stylianou"/><br /><sub><b>Dimitris Stylianou</b></sub></a><br /></td>
  </tr>
</table>

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
