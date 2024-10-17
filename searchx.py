import os
from typing import List, Dict
from dotenv import load_dotenv
from openai import OpenAI
from toolhouse import Toolhouse
import json
import re

# Load environment variables
load_dotenv()

# Set API Keys
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
th = Toolhouse(api_key=os.getenv('TOOLHOUSE_API_KEY'), provider="openai")

# Define the OpenAI model
MODEL = 'gpt-4'

def search_tweets(username: str, max_results: int = 10) -> List[Dict[str, str]]:
    search_query = f"from:{username}"
    messages = [{
        "role": "user",
        "content": f"Search X for the most recent {max_results} tweets {search_query}. Return the results as a JSON array of objects, each with 'id', 'text', and 'date' fields."
    }]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=th.get_tools()
    )

    messages += th.run_tools(response)

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages
    )

    content = response.choices[0].message.content
    print("Raw content:")
    print(content)

    try:
        # Try to extract JSON from the content
        json_match = re.search(r'\[[\s\S]*\]', content)
        if json_match:
            tweets = json.loads(json_match.group())
            if isinstance(tweets, list):
                return tweets
    except json.JSONDecodeError:
        print("Error decoding JSON. Falling back to text parsing.")

    # Fallback: Parse text content if JSON extraction fails
    tweets = []
    lines = content.split('\n')
    current_tweet = {}
    for line in lines:
        if line.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '10.')):
            if current_tweet:
                tweets.append(current_tweet)
                current_tweet = {}
            parts = line.split(': ', 1)
            if len(parts) > 1:
                current_tweet['text'] = parts[1].strip('"')
        elif 'Date:' in line:
            current_tweet['date'] = line.split('Date:', 1)[1].strip()
        elif 'ID:' in line:
            current_tweet['id'] = line.split('ID:', 1)[1].strip()

    if current_tweet:
        tweets.append(current_tweet)

    return tweets

def print_tweets(username: str, tweets: List[Dict[str, str]]):
    print(f"\nHere are some tweets by {username}:")
    for i, tweet in enumerate(tweets, 1):
        print(f"{i}. [Tweet](https://twitter.com/{username}/status/{tweet.get('id', 'N/A')}): \"{tweet.get('text', 'N/A')}\"")
        print(f"   Date: {tweet.get('date', 'N/A')}")
        print()

    print(f"\nTotal tweets retrieved: {len(tweets)}")
    print(f"Search query: from:{username}")

if __name__ == "__main__":
    username = input("Enter the Twitter handle (without @): ")
    max_results = 10
    tweets = search_tweets(username, max_results)
    print_tweets(username, tweets)