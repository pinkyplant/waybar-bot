import os
import json
import praw

# --- REDDIT AUTH ---
reddit = praw.Reddit(
    client_id=os.environ["REDDIT_CLIENT_ID"],
    client_secret=os.environ["REDDIT_CLIENT_SECRET"],
    refresh_token=os.environ["REDDIT_REFRESH_TOKEN"],
    user_agent=os.environ["REDDIT_USER_AGENT"],
)

SUBREDDIT = "waybar"
STATE_FILE = "last_release.json"

# --- GITHUB EVENT ---
with open(os.environ["GITHUB_EVENT_PATH"]) as f:
    event = json.load(f)

release = event["release"]

title = f"Waybar {release['tag_name']} released!"
body = f"{release.get('body', '')}\n\n[View release on GitHub]({release['html_url']})"

subreddit = reddit.subreddit(SUBREDDIT)

# --- Unpin previous release post if tracked ---
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        last = json.load(f)
    try:
        old_post = reddit.submission(last["post_id"])
        old_post.mod.sticky(state=False)
        print(f"Unpinned old post: {old_post.title}")
    except Exception:
        print("No old post to unpin or already deleted.")
else:
    last = {}

# --- Post new release ---
new_post = subreddit.submit(title, selftext=body)
new_post.mod.sticky()
print(f"Pinned new post: {title}")

# --- Save new post ID ---
with open(STATE_FILE, "w") as f:
    json.dump({"post_id": new_post.id}, f)
