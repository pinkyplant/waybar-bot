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
release_id = release["id"]  # unique GitHub release ID

# --- Load last release state ---
if os.path.exists(STATE_FILE):
    with open(STATE_FILE, "r") as f:
        last = json.load(f)
else:
    last = {}

# --- Check if this release was already posted ---
if last.get("release_id") == release_id:
    print("This release was already posted. Exiting.")
    exit(0)

title = f"Waybar {release['tag_name']} released!"
body = f"{release.get('body', '')}\n\n[View release on GitHub]({release['html_url']})"

subreddit = reddit.subreddit(SUBREDDIT)

# --- Unpin previous release post if tracked ---
if "post_id" in last:
    try:
        old_post = reddit.submission(last["post_id"])
        old_post.mod.sticky(state=False)
        print(f"Unpinned old release post: {old_post.title}")
    except Exception:
        print("No old release post to unpin (might have been deleted).")

# --- Post new release ---
new_post = subreddit.submit(title, selftext=body)
new_post.mod.sticky()
print(f"Pinned new release post: {title}")

# --- Save new post info ---
with open(STATE_FILE, "w") as f:
    json.dump({
        "release_id": release_id,
        "post_id": new_post.id
    }, f)
