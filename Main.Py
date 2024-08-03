import praw
import random
import time
import requests
from requests.exceptions import SSLError
import os

# Reddit API credentials
client_id = ' ' # Get this from becoming a developer of reddit api
client_secret = ' ' # Get this from becoming a developer of reddit api
user_agent = 'Test1'
username = 'Username'
password = 'Password'

# Subreddits
source_subreddit = 'Subrred_Name' # Subreddit we are stealing posts from
main_subreddit = 'Subreddit_Name' # Subreddit we are posting to
target_subreddits = [""]  # List of target subreddits for crossposting

# File to store used post IDs
used_posts_file = 'used_posts.txt'

# Initialize Reddit instance
reddit = praw.Reddit(client_id=client_id,
                     client_secret=client_secret,
                     user_agent=user_agent,
                     username=username,
                     password=password)

# We create a file that keeps check of what posts we have already done so we dont repeat
def load_used_posts():
    if os.path.exists(used_posts_file):
        with open(used_posts_file, 'r') as file:
            used_posts = set(line.strip() for line in file)
    else:
        used_posts = set()
    return used_posts

def save_used_posts(used_posts):
    with open(used_posts_file, 'w') as file:
        for post_id in used_posts:
            file.write(f"{post_id}\n")

# Gets random post from the subreddit
def get_random_post(subreddit, used_posts):
    while True:
        try:
            submissions = list(reddit.subreddit(subreddit).hot(limit=100))
            submission = random.choice(submissions)
            if submission.id not in used_posts:
                return submission
        except SSLError as e:
            print(f"SSL Error: {e}")
            time.sleep(60)
        except praw.exceptions.APIException as e:
            print(f"API Exception: {e}")
            time.sleep(60)
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            time.sleep(60)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            time.sleep(60)

def get_gif_url(submission):
    url = submission.url
    if 'redgifs.com' in url:
        return url
    return None

def post_gif_to_main_subreddit(gif_url, title):
    while True:
        try:
            submission = reddit.subreddit(main_subreddit).submit(title, url=gif_url)
            return submission
        except SSLError as e:
            print(f"SSL Error: {e}")
            time.sleep(60)
        except praw.exceptions.APIException as e:
            print(f"API Exception: {e}")
            time.sleep(60)
        except requests.RequestException as e:
            print(f"Request Exception: {e}")
            time.sleep(60)
        except Exception as e:
            print(f"Unexpected Error: {e}")
            time.sleep(60)

# After posting to our subreddit it then crossposts to others, this leads them back to our subreddit
def crosspost_to_subreddits(submission, subreddits):
    for subreddit in subreddits:
        while True:
            try:
                submission.crosspost(subreddit)
                print(f"Crossposted to {subreddit}")
                break
            except praw.exceptions.APIException as e:
                print(f"API Exception: {e}")
                if 'CROSSPOST' in str(e).upper() or 'SUBREDDIT_NOT_ALLOWED' in str(e).upper():
                    print(f"Failed to crosspost to {subreddit}. Skipping this subreddit.")
                    break
                time.sleep(60)
            except SSLError as e:
                print(f"SSL Error: {e}")
                time.sleep(60)
            except requests.RequestException as e:
                print(f"Request Exception: {e}")
                time.sleep(60)
            except Exception as e:
                print(f"Unexpected Error: {e}")
                time.sleep(60)

def main():
    used_posts = load_used_posts()
    while True:
        try:
            random_post = get_random_post(source_subreddit, used_posts)
            if random_post:
                gif_url = get_gif_url(random_post)
                if gif_url:
                    original_title = random_post.title
                    modified_title = original_title
                    submission = post_gif_to_main_subreddit(gif_url, modified_title)
                    if submission:
                        crosspost_to_subreddits(submission, target_subreddits)
                        used_posts.add(random_post.id)
                        save_used_posts(used_posts)
            time.sleep(3600)  # Sleep for 1 hour before posting again
        except Exception as e:
            print(f'Error: {e}')
            time.sleep(600)  # Sleep for 10 minutes before retrying

if __name__ == "__main__":
    main()
