# 🐦 Twitter RSS Feed Generator for @CUSocialMedia
This project fetches the most recent tweets from [@CUSocialMedia](https://x.com/CUSocialMedia) using the Twitter API, formats them into an RSS feed, and displays them on our CampusPress Social Media Lab site using the **RSS Just Better** plugin, styled with custom CSS and JavaScript. It is displayed here:  https://socialmedialab.cornell.edu/news/

---

## The issue: 
X's current privacy policies requires users to log in to X to see tweets. Hence, when we embed the @CUSocialMedia X timeline (via [Twitter Publish](https://publish.twitter.com/#)), the displayed timeline says "No Posts to Show", or entirely disappears.

## Our solution: 
Use the Twitter API to fetch the most recent tweets, format them into an RSS feed, and display them on our WordPress site using the **RSS Just Better** plugin, styled with custom CSS and JavaScript. It is displayed here:  https://socialmedialab.cornell.edu/news/
- 🔁 A **Python script** [`scripts/generate_rss.py`](scripts/generate_rss.py) retrieves the 10 most recent tweets via the Twitter API.
- 📄 Tweets are converted into a styled **RSS feed XML file** [https://cornellsml.github.io/sml-tweets-cache/feeds/cusocialmedia_rss.xml](https://cornellsml.github.io/sml-tweets-cache/feeds/cusocialmedia_rss.xml).
- 🌐 The XML file is **hosted on GitHub Pages**.
- 🕒 A **GitHub Actions cron job** [`.github/workflows/update-rss.yml`](.github/workflows/update-rss.yml) runs the script every 3 days.
- 📥 On CampusPress (WordPress), the RSS feed is displayed using:
  - The **RSS Just Better** plugin
  - **Custom CSS** (WordPress `Advanced Settings → Custom Code → Footer Code`) for styling
  - **Custom JavaScript** (WordPress `Appearance → Custom CSS`) for enhanced interaction