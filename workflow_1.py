import os
from dotenv import load_dotenv
from typing import List
from llama_index.llms.openai import OpenAI

# Load environment variables from .env file
load_dotenv()

class TweetAnalyzer:
    def __init__(self):
        self.llm = OpenAI()

    async def categorize_tweets(self, tweets: List[str]) -> str:
        prompt = f"""Analyze the following tweets and categorize them into interest areas or activities 
        (e.g., fitness, outdoor activities, technology, cooking, hobbies). 
        Provide a comma-separated list of categories:

        Tweets:
        {tweets}

        Categories:"""
        response = await self.llm.acomplete(prompt)
        return str(response).strip()

class InterestMapper:
    def __init__(self):
        self.llm = OpenAI()

    async def map_interests_to_gift_categories(self, interests: str) -> str:
        prompt = f"""For each of the following interest categories, suggest potential gift categories:

        Interest categories:
        {interests}

        Provide a comma-separated list of gift categories:"""
        response = await self.llm.acomplete(prompt)
        return str(response).strip()

class GiftIdeaGenerator:
    def __init__(self):
        self.llm = OpenAI()

    async def generate_affordable_gift_ideas(self, gift_categories: str) -> str:
        prompt = f"""For each of the following gift categories, suggest 2-3 affordable gift ideas under $40:

        Gift categories:
        {gift_categories}

        Provide a comma-separated list of gift ideas:"""
        response = await self.llm.acomplete(prompt)
        return str(response).strip()

class AmazonKeywordGenerator:
    def __init__(self):
        self.llm = OpenAI()

    async def generate_keywords(self, gift_ideas: str) -> List[str]:
        prompt = f"""Based on the following gift ideas, generate Amazon search keywords. 
        Each keyword should be a short phrase suitable for searching on Amazon, 
        and should include "under $40" or a similar price qualifier.

        Gift ideas:
        {gift_ideas}

        Provide a Python list of search keywords:"""
        response = await self.llm.acomplete(prompt)
        # Assuming the response is in the format of a Python list
        return eval(str(response).strip())

async def main():
    # Simulating a list of tweets
    tweets = [
        "Just finished a great workout at the gym!",
        "Can't wait for my camping trip next weekend. Need to get some gear!",
        "Loving my new smartphone. The camera is amazing!",
        "Trying to eat healthier. Any good cookbook recommendations?",
        "Working on a new coding project. Python is so fun!"
    ]

    tweet_analyzer = TweetAnalyzer()
    interest_mapper = InterestMapper()
    gift_idea_generator = GiftIdeaGenerator()
    keyword_generator = AmazonKeywordGenerator()

    # Step 1: Categorize tweets into interests
    interests = await tweet_analyzer.categorize_tweets(tweets)
    print("Interests:", interests)

    # Step 2: Map interests to gift categories
    gift_categories = await interest_mapper.map_interests_to_gift_categories(interests)
    print("Gift Categories:", gift_categories)

    # Step 3: Generate affordable gift ideas
    gift_ideas = await gift_idea_generator.generate_affordable_gift_ideas(gift_categories)
    print("Gift Ideas:", gift_ideas)

    # Step 4: Generate Amazon search keywords
    amazon_keywords = await keyword_generator.generate_keywords(gift_ideas)
    print("Amazon Search Keywords:", amazon_keywords)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())