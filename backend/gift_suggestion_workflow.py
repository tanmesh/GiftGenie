import os
import asyncio
import streamlit as st
from datetime import datetime
from dotenv import load_dotenv
from typing import List
from enum import Enum
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent
)
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.tools import FunctionTool
import sys
import ast
import sys
import traceback
from llama_index.core.workflow import draw_all_possible_flows
from searchx import search_tweets


load_dotenv()

class TweetAnalyzerEvent(Event):
    tweets: List[str]

class InterestMapperEvent(Event):
    interests: str

class GiftIdeaGeneratorEvent(Event):
    gift_categories: str

class GiftDebaterEvent(Event):
    gift_ideas: str

class GiftReasonerEvent(Event):
    debates: str

class AmazonKeywordGeneratorEvent(Event):
    gift_ideas: List[str]

class AmazonProductLinksEvent(Event):
    product_links: str
    product_image: str
    product_title: str
    product_price: str
    product_rating: str

class GiftSuggestionWorkflow(Workflow):
    def __init__(self, price_ceiling: float, log_print_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_ceiling = price_ceiling
        self.log_print = log_print_func

    @staticmethod
    def extract_amazon_product_links(keyword: str):
        from apify_client import ApifyClient
        import os
        from dotenv import load_dotenv
        import urllib.parse

        # Initialize the ApifyClient with your API token
        load_dotenv()

        api_token = os.getenv("APIFY_API_TOKEN")
        client = ApifyClient(api_token)

        keyword = urllib.parse.quote(keyword, safe="")
        # Prepare the Actor input
        run_input = {
            "categoryOrProductUrls": [{"url": f"https://www.amazon.com/s?k={keyword}"}],
            "maxItemsPerStartUrl": 1,
            "proxyCountry": "AUTO_SELECT_PROXY_COUNTRY",
            "maxOffers": 0,
            "scrapeSellers": False,
            "useCaptchaSolver": False,
            "scrapeProductVariantPrices": False,
        }

        print(f"Running Actor with input: {run_input}")

        try:
            # Run the Actor and wait for it to finish
            run = client.actor("BG3WDrGdteHgZgbPK").call(run_input=run_input)

            # Fetch Actor results from the run's dataset
            data = client.dataset(run["defaultDatasetId"]).list_items().items
            for item in data:
                print(f'Item: {item}')

            return data
        except Exception as e:
            print(f"An error occurred: {str(e)}")
            traceback.print_exc()
            return []

    @step(pass_context=True)
    async def amazon_product_link_generator(self, ctx: Context, ev: Event) -> AmazonProductLinksEvent:
        print(f"Generating product links for keyword")
        print(f'Ev: {ev}')
        product_links = self.extract_amazon_product_links(ev)
        
        print("\n--- Amazon Product Links ---")
        for link in product_links:
            print(link)
        print("----------------------------\n")

        if not product_links:
            print("No product links found.")
            return Event(product_links=None, product_image=None, product_title=None, product_price=None, product_rating=None)

        product_link = product_links[0]

        # product_link =  {'title': 'PopSockets Phone Grip with Expanding Kickstand, Underworld Skull', 'url': 'https://www.amazon.com/dp/B07ZKRZRY1', 'asin': 'B07ZKRZRY1', 'price': {'value': 7.5, 'currency': '$'}, 'inStock': True, 'inStockText': 'In Stock  In Stock', 'listPrice': {'value': 9.99, 'currency': '$'}, 'brand': 'PopSockets', 'author': None, 'shippingPrice': None, 'stars': 4.7, 'starsBreakdown': {'5star': 0.86, '4star': 0.07, '3star': 0.03, '2star': 0.01, '1star': 0.03}, 'reviewsCount': 8055, 'answeredQuestions': None, 'breadCrumbs': 'Cell Phones & Accessories › Accessories › Grips', 'thumbnailImage': 'https://m.media-amazon.com/images/I/618NCkBT8SL.__AC_SX300_SY300_QL70_ML2_.jpg', 'galleryThumbnails': ['https://m.media-amazon.com/images/I/41ytV9Uus7L._AC_SR38.jpg', 'https://m.media-amazon.com/images/I/41UYscOa8xL._AC_SR38.jpg', 'https://m.media-amazon.com/images/I/51b29jds5lL._AC_SR38.jpg', 'https://m.media-amazon.com/images/I/31sm9ur3TwL._AC_SR38.jpg', 'https://m.media-amazon.com/images/I/31IJF26GMUL._AC_SR38.jpg', 'https://m.media-amazon.com/images/I/41DcsKA+WAL._AC_SR38.jpg'], 'highResolutionImages': ['https://m.media-amazon.com/images/I/618NCkBT8SL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/617pFyg6NuL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/61x1qFZLpEL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/418DcsRikSL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41fwKFcLr-L._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/61T-o17H0bL._AC_SL1000_.jpg'], 'description': None, 'features': ['- Our durable Pop Socket compatible with iPhone, Samsung, and any other devices, we call a “PopGrip” is anti-drop, allows for one-handed use of your device, and the ability to prop up your phone wherever you go', '- A little life-changer people like to call: a cell phone holder, phone gripper for back of phone, phone holder for hand, or whichever you name you decide', '- PopSockets are compatible with all Popsocket phone accessories including wallets, cases, mounts, slides, and non-Popsocket cases for phones', '- Change up your PopGrip style without replacing the whole grip and swap out the top for one of our PopTops. Just press flat, turn 90 degrees until you hear a click and swap', '- Stick on with the adhesive and reposition as needed. Pop Sockets stick best to smooth hard plastic cases (may not stick to silicone, soft, or waterproof cases)'], 'attributes': [], 'productOverview': [{'key': 'Brand', 'value': 'PopSockets'}, {'key': 'Color', 'value': 'Underworld'}, {'key': 'Special Feature', 'value': ''}, {'key': 'Material', 'value': 'Polycarbonate (PC)'}, {'key': 'Grip Type', 'value': 'Pop Grip'}], 'variantAsins': ['B09SZRQGWZ', 'B08WVVLZVQ', 'B07ZKRMJDZ', 'B07ZKRZRY1', 'B09SZRZYTN', 'B09T1JSQL1', 'B08DTG2Z1G', 'B08DRYSR4Z'], 'variantDetails': [{'name': 'Balance Drip small', 'thumbnail': 'https://m.media-amazon.com/images/I/41VKK-wJaKL._AC_SR38.jpg', 'images': ['https://m.media-amazon.com/images/I/51qGOz5y+vL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51yBg9MuDbL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/510hieoiTxL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41niLUbDiLL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41Oms+IG2CL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41RjBwjMi3L._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/415hmPn-EuL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51G0sop2UUL._AC_SL1000_.jpg'], 'asin': 'B09SZRQGWZ', 'price': None}, {'name': 'Skull small', 'thumbnail': 'https://m.media-amazon.com/images/I/41q8Fwsn18S._AC_SR38.jpg', 'images': ['https://m.media-amazon.com/images/I/61FJv8RLuZS._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/61VuMKBjoNS._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51c06I5SozS._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41VAfX5IqwS._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41mQFxB+VUS._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51W-GInW68L._AC_SL1000_.jpg'], 'asin': 'B08WVVLZVQ', 'price': None}, {'name': 'Sabertooth small', 'thumbnail': 'https://m.media-amazon.com/images/I/51tS-wu8UDL._AC_SR38.jpg', 'images': ['https://m.media-amazon.com/images/I/81BLd1H1kAL._AC_SL1478_.jpg', 'https://m.media-amazon.com/images/I/71RYPfTQmvL._AC_SL1500_.jpg', 'https://m.media-amazon.com/images/I/71lg1uFZKqL._AC_SL1332_.jpg', 'https://m.media-amazon.com/images/I/71AF4dFCHTL._AC_SL1452_.jpg', 'https://m.media-amazon.com/images/I/61ix6Ur3vrL._AC_SL1500_.jpg', 'https://m.media-amazon.com/images/I/61uq9h3anyL._AC_SL1500_.jpg'], 'asin': 'B07ZKRMJDZ', 'price': {'value': 9.99, 'currency': '$'}}, {'name': 'Underworld small', 'thumbnail': 'https://m.media-amazon.com/images/I/41ytV9Uus7L._AC_SR38.jpg', 'images': ['https://m.media-amazon.com/images/I/618NCkBT8SL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/617pFyg6NuL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/61x1qFZLpEL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/418DcsRikSL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41fwKFcLr-L._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/61T-o17H0bL._AC_SL1000_.jpg'], 'asin': 'B07ZKRZRY1', 'price': {'value': 7.5, 'currency': '$'}}, {'name': 'Delirious small', 'thumbnail': 'https://m.media-amazon.com/images/I/41GnuBQCSqL._AC_SR38.jpg', 'images': ['https://m.media-amazon.com/images/I/61h291TpIOL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/61UXAgHfm7L._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/517U2XYXTaL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41VAzqHAesL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41+4FUCccIL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41774Yjxv7L._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/410oVsBuAuL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/519Ls7JEY+L._AC_SL1000_.jpg'], 'asin': 'B09SZRZYTN', 'price': {'value': 7.5, 'currency': '$'}}, {'name': 'Yin Yang small', 'thumbnail': 'https://m.media-amazon.com/images/I/41pnjiNz6ZL._AC_SR38.jpg', 'images': ['https://m.media-amazon.com/images/I/51aPB4iVCnL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/518dFhAtvEL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51lZlsb0gSL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41AiZSAfjwL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41BiKs414mL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51iMWTuekDL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51P3LT1shKL._AC_SL1000_.jpg'], 'asin': 'B09T1JSQL1', 'price': {'value': 14.99, 'currency': '$'}}, {'name': 'Evil Eye small', 'thumbnail': 'https://m.media-amazon.com/images/I/51bZk5J3QcL._AC_SR38.jpg', 'images': ['https://m.media-amazon.com/images/I/61CDpY+inKL._AC_SL1100_.jpg', 'https://m.media-amazon.com/images/I/61hsHqJdk6L._AC_.jpg', 'https://m.media-amazon.com/images/I/51-r8WGlj-L._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51NR--ZZaOL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/61OSXjYInBL._AC_SL1020_.jpg', 'https://m.media-amazon.com/images/I/51kNUb2W5JL._AC_SL1000_.jpg'], 'asin': 'B08DTG2Z1G', 'price': {'value': 16.9, 'currency': '$'}}, {'name': 'Shaky Bones small', 'thumbnail': 'https://m.media-amazon.com/images/I/41Uuug7tJ+L._AC_SR38.jpg', 'images': ['https://m.media-amazon.com/images/I/61bh4nk6u7L._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/510R1aYRmGL._AC_.jpg', 'https://m.media-amazon.com/images/I/51KCq7hzSTL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51vam1nBnBL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/417eq0dB9lL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41hIYK9hzdL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41o61O4B1SL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/41N7HjiNHML._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/51KVlolqLkL._AC_SL1000_.jpg', 'https://m.media-amazon.com/images/I/61bh4nk6u7L._AC_SL1000_.jpg'], 'asin': 'B08DRYSR4Z', 'price': None}], 'reviewsLink': 'https://www.amazon.com/product-reviews/B07ZKRZRY1', 'hasReviews': True, 'delivery': 'Wednesday, October 30', 'fastestDelivery': 'Friday, November 1', 'returnPolicy': None, 'support': None, 'variantAttributes': [{'key': 'Color', 'value': 'Underworld'}, {'key': 'Size', 'value': 'small'}], 'manufacturerAttributes': [], 'seller': {'id': None, 'url': 'https://www.amazon.com', 'name': 'Amazon.com', 'businessName': 'Amazon.com, Inc.', 'phone': '1-206-266-1000', 'address': ['410 Terry Ave N', 'Seattle', 'WA', '98109', 'US']}, 'bestsellerRanks': None, 'isAmazonChoice': True, 'amazonChoiceText': None, 'bookDescription': None, 'priceRange': None, 'aPlusContent': None, 'aiReviewsSummary': None, 'locationText': 'Update location', 'loadedCountryCode': 'US', 'offers': [], 'unNormalizedProductUrl': 'https://www.amazon.com/s?k=%5BBudget-friendly%20Phone%20Accessories%20under%20%2440%5D%28https%3A%2F%2Fwww.amazon.com%2Fs%3Fk%3DBudget-friendly%2BPhone%2BAccessories%2Bunder%2B40%29', 'categoryPageData': {'saleSummary': None, 'isSponsored': True, 'productPosition': 1}}

        return AmazonProductLinksEvent(
            product_links=product_link.get('url', ''),
            product_image=product_link.get('thumbnailImage', ''),
            product_title=product_link.get('title', ''),
            product_price=str(product_link.get('price', {}).get('value', 'N/A')) if product_link.get('price') else 'N/A',
            product_rating=str(product_link.get('stars', 'N/A'))
        )

    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: StartEvent) -> TweetAnalyzerEvent:
        self.log_print("Step: Get Tweets and Compile Text")
        ctx.data["llm"] = OpenAI(model="gpt-4", temperature=0.4)
        
        tweets = ctx.data.get("tweets", [])
        additional_text = ctx.data.get("additional_text", "")
        
        # If no tweets from Twitter handle or if an error occurred, use default tweets
        if not tweets:
            tweets = [
                "Just finished a great workout at the gym!",
                "Can't wait for my camping trip next weekend. Need to get some gear!",
                "Loving my new smartphone. The camera is amazing!",
                "Trying to eat healthier. Any good cookbook recommendations?",
                "Working on a new coding project. Python is so fun!"
            ]
        
        # Add additional text if provided
        if additional_text:
            tweets.append(additional_text)
        
        self.log_print(f"Tweets and additional text compiled: {tweets}")
        return TweetAnalyzerEvent(tweets=tweets) 

    @step(pass_context=True)
    async def tweet_analyzer(self, ctx: Context, ev: TweetAnalyzerEvent) -> InterestMapperEvent:
        self.log_print("Step: Tweet Analyzer")
        if "tweet_analyzer_agent" not in ctx.data:
            def categorize_tweets(tweets: List[str]) -> str:
                prompt = f"""Analyze the following tweets and categorize them into interest areas or activities. 
                Provide a comma-separated list of categories:

                Tweets:
                {tweets}

                Categories:"""
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip()

            system_prompt = """
                You are an AI assistant that analyzes tweets and categorizes them into interest areas or activities.
                Your task is to provide a comma-separated list of categories based on the given tweets.
            """

            ctx.data["tweet_analyzer_agent"] = create_agent(ctx, [categorize_tweets], system_prompt)

        interests = ctx.data["tweet_analyzer_agent"].chat(f"Analyze these tweets: {ev.tweets}, and give response in Markdown format.")
        self.log_print(f"Interests identified: {str(interests)}")
        return InterestMapperEvent(interests=str(interests))

    @step(pass_context=True)
    async def interest_mapper(self, ctx: Context, ev: InterestMapperEvent) -> GiftIdeaGeneratorEvent:
        if "interest_mapper_agent" not in ctx.data:
            def map_interests_to_gift_categories(interests: str) -> str:
                prompt = f"""For each of the following interest categories, suggest potential gift categories:

                Interest categories:
                {interests}

                Provide a comma-separated list of gift categories:"""
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip()

            system_prompt = """
                You are an AI assistant specializing in mapping interest categories to potential gift categories. Your primary task is to generate a diverse and relevant list of gift categories based on given interests. Follow these guidelines:

                Analyze the provided interest categories carefully.
                Generate a list of at least 10 gift categories that align with these interests.
                Ensure each gift category is:

                Specific enough to be useful for gift searching
                Broad enough to encompass multiple gift options
                Relevant to the given interests
                Suitable for various age groups and genders, unless specified otherwise


                Consider both obvious and less conventional gift categories that might appeal to enthusiasts in the given interest areas.
                Include a mix of practical, entertaining, and educational gift categories when appropriate.
                Avoid overly broad categories like "electronics" or "books" unless the interests are very general.
                Format your response as a comma-separated list of gift categories, without numbering or bullet points.

                Example:
                Input: "Outdoor activities, photography"
                Output: hiking gear, weatherproof camera bags, adventure photography workshops, lightweight tripods
                Remember to tailor your responses to the specific interests provided and aim for a balance between creativity and practicality in your gift category suggestions.
            """

            ctx.data["interest_mapper_agent"] = create_agent(ctx, [map_interests_to_gift_categories], system_prompt)

        gift_categories = ctx.data["interest_mapper_agent"].chat(f"Map these interests to gift categories: {ev.interests}, and give response in Markdown format.")
        print("\n--- Gift Categories ---")
        print(str(gift_categories))
        print("--------------------\n")
        self.log_print(f"Gift Categories: {str(gift_categories)}")
        return GiftIdeaGeneratorEvent(gift_categories=str(gift_categories))

    @step(pass_context=True)
    async def gift_idea_generator(self, ctx: Context, ev: GiftIdeaGeneratorEvent) -> GiftDebaterEvent:
        if "gift_idea_generator_agent" not in ctx.data:
            def generate_affordable_gift_ideas(gift_categories: str) -> str:
                prompt = f"""For each of the following gift categories, suggest gift ideas under 
                ${self.price_ceiling}. Always recommend 10 items in total, including perishable 
                boutique pantry items like pumpkin seed butter or fancy trail mix. Provide a comma-separated 
                list of 10 gift ideas:

                Gift categories:
                {gift_categories}"""
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip()

            system_prompt = f"""
                You are an AI assistant that generates affordable gift ideas based on gift categories.
                Your task is to provide a comma-separated list of 10 gift ideas under ${self.price_ceiling}, including some perishable boutique pantry items.
                Be specific about the gift idea item. "Tech gadgets" are too broad, consider a "smart fitness monitor watch" instead.
                Default to charcuterie gift baskets, artisan chocolates, specialty foods such as high quality seed butters, preserves of
                a high-quality olives or canned fish. Organic, zero-waste, family-owned businesses, sustainable products are always a better
                choice across any category. 
            """

            ctx.data["gift_idea_generator_agent"] = create_agent(ctx, [generate_affordable_gift_ideas], system_prompt)

        gift_ideas = ctx.data["gift_idea_generator_agent"].chat(f"Generate gift ideas for these categories: {ev.gift_categories}, and give response in Markdown format.")
        print("\n--- Gift Ideas ---")
        print(str(gift_ideas))
        print("--------------------\n")
        self.log_print(f"Gift Ideas: {str(gift_ideas)}")
        return GiftDebaterEvent(gift_ideas=str(gift_ideas))


    @step(pass_context=True)
    async def gift_debater(self, ctx: Context, ev: GiftDebaterEvent) -> GiftReasonerEvent:
        if "gift_debater_agent" not in ctx.data:
            def debate_gift_ideas(gift_ideas: str) -> str:
                prompt = f"""Debate the following gift ideas as Christmas gifts under $40. For each gift idea, provide a structured debate between LLM1 (For) and LLM2 (Against). Consider these factors:

                1. Alignment with recipient's interests
                2. Practicality and usefulness
                3. Appropriateness for recipient's age, gender, lifestyle, and demographic
                4. Potential reasons the recipient might not appreciate the gift
                5. Perishability and longevity of the gift

                Gift ideas:
                {gift_ideas}

                Debate format:
                [Gift Idea]
                LLM1 (For): [Argument in favor]
                LLM2 (Against): [Counter-argument]
                LLM1 (For): [Rebuttal]
                LLM2 (Against): [Final point]

                Please provide a structured debate for each gift idea:
                """
                return ctx.data["llm"].complete(prompt)

            system_prompt = """
                You are an AI assistant that facilitates debates on gift ideas. Your role is to:
                1. Present balanced arguments for and against each gift idea.
                2. Maintain a consistent debate structure for each gift.
                3. Ensure that LLM1 always argues in favor of the gift, while LLM2 argues against it.
                4. Keep each speaker's turn concise and focused on a single point.
                5. Ensure that the debate covers multiple aspects of the gift's suitability.
                """

            ctx.data["gift_debater_agent"] = create_agent(ctx, [debate_gift_ideas], system_prompt)

            debates = ctx.data["gift_debater_agent"].chat(f"Debate these gift ideas: {ev.gift_ideas}, and give response in Markdown format.")
            
            print("\n--- Gift Debates ---")
            print(str(debates))
            print("--------------------\n")
            self.log_print(f"Gift Debates: {str(debates)}")
            return GiftReasonerEvent(debates=str(debates))

    @step(pass_context=True)
    async def gift_reasoner(self, ctx: Context, ev: GiftReasonerEvent) -> AmazonKeywordGeneratorEvent:
        if "gift_reasoner_agent" not in ctx.data:
            def reason_over_debates(debates: str) -> List[str]:
                prompt = f"""Based on the following debates, reason over the arguments and select the 3 best specific gift items. 
                Provide a final take on why these 3 were chosen:

                Debates:
                {debates}

                Selected Gifts:
                1. [SPECIFIC_GIFT_ITEM_1]
                Rationale: [CONCISE_EXPLANATION_1]

                2. [SPECIFIC_GIFT_ITEM_2]
                Rationale: [CONCISE_EXPLANATION_2]

                3. [SPECIFIC_GIFT_ITEM_3]
                Rationale: [CONCISE_EXPLANATION_3]
                """
                
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip().split('\n')

            system_prompt = """
                You are an AI assistant that reasons over gift idea debates and selects specific gift items.
                Your task is to analyze the debates, select the 3 best specific gift items (not general categories),
                and provide concise rationales for your choices. Ensure your selections are diverse and cater to 
                different aspects of the recipient's interests or needs.
            """

            ctx.data["gift_reasoner_agent"] = create_agent(ctx, [reason_over_debates], system_prompt)

        final_gifts = ctx.data["gift_reasoner_agent"].chat(f"Reason over these debates: {ev.debates}, and give response in Markdown format.")
        
        # Print the final gift selections for the user to see
        print("\n--- Final Gift Selections ---")
        print(str(final_gifts))
        print("------------------------------\n")

        # Convert the AgentChatResponse to a list of strings
        gift_list = str(final_gifts).strip().split('\n')
        self.log_print(f"Final Gift Selections: {str(final_gifts)}")
        return AmazonKeywordGeneratorEvent(gift_ideas=gift_list)

    @step(pass_context=True)
    async def amazon_keyword_generator(self, ctx: Context, ev: AmazonKeywordGeneratorEvent) -> StopEvent:
        if "amazon_keyword_generator_agent" not in ctx.data:

            def generate_keywords(gift_ideas: List[str]) -> List[str]:
                prompt = f"""Based on the following gift ideas, generate Amazon search keywords. 
                Each keyword should be a short phrase suitable for searching on Amazon, 
                and should include "under $40" or a similar price qualifier.

                Gift ideas:
                {', '.join(gift_ideas)}

                Provide a Python list of 3 search keywords:"""
                response = ctx.data["llm"].complete(prompt)
                return eval(str(response).strip())

            system_prompt = """
                You are an AI assistant that generates Amazon search keywords based on gift ideas.
                Your task is to provide a list of 3 search keywords suitable for Amazon, including a price qualifier.
            """

            ctx.data["amazon_keyword_generator_agent"] = create_agent(
                ctx, [generate_keywords], system_prompt
            )

        amazon_keywords = ctx.data["amazon_keyword_generator_agent"].chat(
            f"Generate keywords for these gift ideas: {ev.gift_ideas} and give response in Markdown format."
        )
                
        # Extract the content from the AgentChatResponse
        response_text = amazon_keywords.response.strip()
        
        # Parse the keywords from the response text
        keywords_list = []
        for line in response_text.split('\n'):
            if line.strip().startswith(('- ', '• ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ')):
                keywords_list.append(line.strip().split(' ', 1)[1])
        
        # Ensure we have at least one keyword
        if not keywords_list:
            st.error("Failed to generate valid keywords. Please try again.")
            keywords_list = ["Gift under $40"]  # Fallback keyword
        
        # # Display the generated Amazon keywords
        # st.subheader("Amazon Search Keywords")
        # for keyword in keywords_list:
        #     st.write(f"- {keyword}")

        return AmazonKeywordGeneratorEvent(gift_ideas=ev.gift_ideas, amazon_keywords=keywords_list)

def create_agent(ctx: Context, tools: List[callable], system_prompt: str):
    function_tools = [FunctionTool.from_defaults(fn=tool) for tool in tools]
    agent_worker = FunctionCallingAgentWorker.from_tools(
        tools=function_tools,
        llm=ctx.data["llm"],
        allow_parallel_tool_calls=False,
        system_prompt=system_prompt
    )
    # draw_all_possible_flows(GiftSuggestionWorkflow, filename="trivial_workflow.html")
    return agent_worker.as_agent()

async def main():
    price_ceiling = 30

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M") + ".txt"
    log_path = os.path.join(log_dir, log_filename)

    def log_print(*args, **kwargs):
        message = " ".join(map(str, args))
        print(message, flush=True)  # Print to console immediately
        with open(log_path, "a") as log_file:
            log_file.write(message + "\n")
            log_file.flush()  # Ensure it's written to the file immediately

    sys.excepthook = lambda type, value, tb: log_print("".join(traceback.format_exception(type, value, tb)))

    try:
        log_print(f"Starting workflow with price ceiling: ${price_ceiling}")
        workflow = GiftSuggestionWorkflow(price_ceiling=price_ceiling, log_print_func=log_print, timeout=1200, verbose=True)
        result = await workflow.run()
        # draw_all_possible_flows(GiftSuggestionWorkflow, filename="trivial_workflow.html")
        log_print(result)
    except Exception as e:
        log_print(f"An error occurred: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    finally:
        log_print(f"Log saved to: {log_path}")

if __name__ == "__main__":
    asyncio.run(main())