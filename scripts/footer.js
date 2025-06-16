// Custom JavaScript for the footer of the Cornell Social Media Lab website
// This script processes the RSS feed from Twitter and formats it for display
// Found in Advanced Settings > Custom Code > Footer Code

// Unused function 
// Replace mentions, hashtags, and URLs with links
function linkifyText(text) {
  return text
    .replace(/(https?:\/\/[^\s]+)/g, url => {
      return `<a href="${url}" target="_blank">${url}</a>`;
    })
    .replace(/@(\w+)/g, (match, username) => {
      return `<a href="https://twitter.com/${username}" target="_blank">@${username}</a>`;
    })
    .replace(/#(\w+)/g, (match, tag) => {
      return `<a href="https://twitter.com/hashtag/${tag}" target="_blank">#${tag}</a>`;
    });
}

// Replace escaped HTML tags with actual HTML
// This function is used to convert escaped HTML entities back to actual HTML tags
function embedHTML(text) {
  return text
    // Replace escaped <a href="...">...</a>
    .replace(
      /&lt;a\s+href="([^"]+)"(?:\s+target="_blank")?&gt;([\s\S]*?)&lt;\/a&gt;/g,
      (match, href, linkText) => `<a href="${href}" target="_blank">${linkText}</a>`
    )
    // Replace escaped <img ... style="max-width:..."> elements
    .replace(
      /&lt;img\s+src="([^"]+)"[^&]*style="([^"]*)"[^&]*\/?&gt;/g,
      (match, src, style) => `<img src="${src}" style="${style}" alt="" />`
    )
    // Replace escaped <br>
    .replace(/&lt;br\s*\/?&gt;/g, '<br />');
}

document.addEventListener("DOMContentLoaded", function () {
  const avatarUrl = "https://pbs.twimg.com/profile_images/925703062823596033/qlOe4WtP_400x400.jpg"; // Your avatar

  const tweets = document.querySelectorAll(".rssjb li");

  tweets.forEach(tweet => {
    const originalLink = tweet.querySelector("a.title");
    const originalText = originalLink.textContent.trim();

    const avatarWrapper = tweet.querySelector(".avatar-wrapper") || document.createElement("div");
    avatarWrapper.classList.add("avatar-wrapper");
    if (!avatarWrapper.querySelector("img")) {
      avatarWrapper.innerHTML = `<img src="${avatarUrl}" alt="Profile Avatar" class="avatar">`;
      tweet.prepend(avatarWrapper);
    }

    const tweetContentWrapper = document.createElement("div");
    tweetContentWrapper.className = "tweet-content-wrapper";

    const linkedText = embedHTML(originalText);
    const p = document.createElement("p");
    p.className = "title";
    p.innerHTML = linkedText;

    const dateSpans = tweet.querySelectorAll(".datetime");
    dateSpans.forEach(span => tweetContentWrapper.appendChild(span));

    const tweetDate = dateSpans[0]?.textContent || ""; // Grab the date span if available
    const userLine = document.createElement("p");
    userLine.className = "username"; 
    userLine.innerHTML = `<a href="https://twitter.com/CUSocialMedia" target="_blank">Cornell Social Media Lab</a><span style="color:gray;">  @CUSocialMedia</span>`;

    tweetContentWrapper.prepend(p);
    tweetContentWrapper.prepend(userLine);

    const clonedTweet = tweet.cloneNode(false); // just <li>
    clonedTweet.appendChild(avatarWrapper);
    clonedTweet.appendChild(tweetContentWrapper);

    const linkWrapper = document.createElement("a");
    linkWrapper.href = originalLink.href;
    linkWrapper.target = "_blank";
    linkWrapper.className = "tweet-wrapper-link";
    linkWrapper.style.textDecoration = "none";
    linkWrapper.style.color = "inherit";

    linkWrapper.appendChild(clonedTweet);
    tweet.replaceWith(linkWrapper);
  });
  const element = document.getElementById('secondary-nav'); // Get the element by its ID
  element.style.visibility = 'visible'; // Set the visibility property to 'hidden'
});