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
      return `<a href="https://twitter.com/${username}" class="twitter-username" target="_blank">@${username}</a>`;
    })
    .replace(/#(\w+)/g, (match, tag) => {
      return `<a href="https://twitter.com/hashtag/${tag}" target="_blank">#${tag}</a>`;
    });
}

function embedHTML(text) {
  // 1. Decode all HTML entities (e.g., &lt; &#8594; <)
  const decode = document.createElement("textarea");
  decode.innerHTML = text;
  const decoded = decode.value;

  // 2. Parse the decoded string as real HTML
  const wrapper = document.createElement("div");
  wrapper.innerHTML = decoded;

  // 3. Add class="twitter-username" to ALL links found inside
  wrapper.querySelectorAll("a").forEach(a => {
    a.classList.add("twitter-username");
    a.target = "_blank";
  });

  return wrapper.innerHTML;
}

document.addEventListener("DOMContentLoaded", function () {
  const avatarUrl = "https://pbs.twimg.com/profile_images/925703062823596033/qlOe4WtP_400x400.jpg";

  const tweets = document.querySelectorAll(".rssjb li");

  tweets.forEach(tweet => {
    const originalLink = tweet.querySelector("a.title");

    // IMPORTANT: use innerHTML so escaped RSS content is preserved
    const originalText = originalLink.innerHTML.trim();

    // --- avatar wrapper ---
    const avatarWrapper = tweet.querySelector(".avatar-wrapper") || document.createElement("div");
    avatarWrapper.classList.add("avatar-wrapper");

    if (!avatarWrapper.querySelector("img")) {
      avatarWrapper.innerHTML = `<img src="${avatarUrl}" alt="Profile Avatar" class="avatar">`;
      tweet.prepend(avatarWrapper);
    }

    // --- tweet content wrapper ---
    const tweetContentWrapper = document.createElement("div");
    tweetContentWrapper.className = "tweet-content-wrapper";

    // embed HTML (unescape everything + add twitter-username to all <a>)
    const linkedText = embedHTML(originalText);

    const p = document.createElement("p");
    p.className = "title";
    p.innerHTML = linkedText;

    // --- date spans ---
    const dateSpans = tweet.querySelectorAll(".datetime");
    dateSpans.forEach(span => tweetContentWrapper.appendChild(span));

    // --- Username line at top ---
    const userLine = document.createElement("p");
    userLine.className = "username";
    userLine.innerHTML =
      `<a href="https://twitter.com/CUSocialMedia" target="_blank" class="twitter-username">Cornell Social Media Lab</a>
       <span style="color:gray;"> @CUSocialMedia</span>`;

    // Order: username &#8594; text &#8594; date
    tweetContentWrapper.prepend(p);
    tweetContentWrapper.prepend(userLine);

    // --- clone <li> shell ---
    const clonedTweet = tweet.cloneNode(false);
    clonedTweet.appendChild(avatarWrapper);
    clonedTweet.appendChild(tweetContentWrapper);

    // --- link wrapper for the whole tweet ---
    const linkWrapper = document.createElement("a");
    linkWrapper.href = originalLink.href;
    linkWrapper.target = "_blank";
    linkWrapper.className = "tweet-wrapper-link";
    linkWrapper.style.textDecoration = "none";
    linkWrapper.style.color = "inherit";

    linkWrapper.appendChild(clonedTweet);
    tweet.replaceWith(linkWrapper);
  });

  // Reveal secondary nav after tweets are processed
  const element = document.getElementById('secondary-nav');
  element.style.visibility = 'visible';
});