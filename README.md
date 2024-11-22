# Discord RSS Announcement Bot

## Description
This bot fetches announcements from a university's eClass announcements section (via RSS) and posts them in a Discord channel using webhooks.

The current implementation in `announcements-bot.py`, specifically the function [`fetch_announcements`](app/announcements-bot.py#L60-L112),
is tailored to handle the data structure of the [RSS feed](https://thales.cs.unipi.gr/modules/announcements/rss.php?c=TMG118) of the
[eClass system](https://thales.cs.unipi.gr/modules/announcements/?course=TMG118) used by the _University of Piraeus - Department of Informatics_.

To use the script with other RSS-supported websites, you will need to modify the logic in [`fetch_announcements`](app/announcements-bot.py#L60-L112)
to match the RSS feed structure of the target website.

## Features
- Fetches announcements automatically from the university eClass RSS feed.
- Posts them directly to Discord via webhooks.
- Provides easy configuration and customization for your specific RSS feed and Discord server.

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
