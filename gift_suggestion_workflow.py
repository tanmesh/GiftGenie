from typing import List, Dict
import re
from llama_index.llms.openai import OpenAI
import os
import asyncio
from datetime import datetime
from typing import List
from llama_index.llms.openai import OpenAI
from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent
)
from llama_index.core.agent import FunctionCallingAgentWorker
from llama_index.core.tools import FunctionTool
import sys
import ast
import traceback
from typing import List, Dict, Optional
from llama_index.core.workflow import Event
import sys
import json
import random


class InitializeEvent(Event):
    pass

class TweetAnalyzerEvent(Event):
    tweets: List[str]

class InterestMapperEvent(Event):
    interests: str

class GiftIdeaGeneratorEvent(Event):
    gift_categories: str

class MediationEvent(Event):
    gift_ideas: List[str]

class GiftDebaterEvent(Event):
    gift_ideas: List[str]
    debates: Dict[str, Dict[str, str]]

class GiftReasonerEvent(Event):
    gift_ideas: Dict[str, List[str]]

class AmazonKeywordGeneratorEvent(Event):
    gift_ideas: List[str]
    amazon_keywords: List[str] = []

class AmazonKeywordEvent(Event):
    amazon_keywords: List[str]

class AmazonProductLinkEvent(Event):
    keyword: str

class ProductLinkEvent(Event):
    product_title: str
    product_price: Optional[float] = None
    product_rating: Optional[float] = None
    product_image: str
    product_links: str

class GiftSuggestionWorkflow(Workflow):
    def __init__(self, price_ceiling: float, log_print_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_ceiling = price_ceiling
        self.log_print = log_print_func

    def create_agent(self, ctx: Context, tools: List[callable], system_prompt: str):
        function_tools = [FunctionTool.from_defaults(fn=tool) for tool in tools]
        agent_worker = FunctionCallingAgentWorker.from_tools(
            tools=function_tools,
            llm=ctx.data["llm"],
            allow_parallel_tool_calls=False,
            system_prompt=system_prompt
        )
        return agent_worker.as_agent()

    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: StartEvent) -> TweetAnalyzerEvent:
        self.log_print("Step: Initialize and Get Tweets")
        ctx.data["llm"] = OpenAI(model="gpt-4", temperature=0.4)
        
        raw_tweets = ctx.data.get("tweets", [])
        processed_tweets = []

        for tweet in raw_tweets:
            try:
                tweet_data = json.loads(tweet)
                processed_tweets.append(tweet_data['text'])
            except json.JSONDecodeError:
                # If JSON parsing fails, assume it's already a string and add it directly
                processed_tweets.append(tweet)

        if not processed_tweets:
            processed_tweets = [
                "Just finished a great workout at the gym!",
                "Can't wait for my camping trip next weekend. Need to get some gear!",
                "Loving my new smartphone. The camera is amazing!",
                "Trying to eat healthier. Any good cookbook recommendations?",
                "Working on a new coding project. Python is so fun!"
            ]
        
        additional_text = ctx.data.get("additional_text", "")
        if additional_text:
            processed_tweets.append(additional_text)
        
        self.log_print(f"Tweets and additional text compiled: {processed_tweets}")
        return TweetAnalyzerEvent(tweets=processed_tweets)

    @step(pass_context=True)
    async def tweet_analyzer(self, ctx: Context, ev: TweetAnalyzerEvent) -> InterestMapperEvent:
        self.log_print("Step: Tweet Analyzer")
        if "tweet_analyzer_agent" not in ctx.data:
            def categorize_tweets(tweets: List[str]) -> str:
                prompt = f"""Analyze the following tweets and categorize them into interest areas or activities. 
                If you can't determine specific interests, use these default categories: Technology,  Self-Care, Travel, Food, Fitness.
                Provide a comma-separated list of at least 5 categories:

                Tweets:
                {tweets}

                Categories:"""
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip()

            system_prompt = """
                You are an AI assistant that analyzes tweets and categorizes them into interest areas or activities.
                Your task is to provide a comma-separated list of at least 5 categories based on the given tweets.
                If you can't determine specific interests from the tweets, use these default categories: 
                Technology, Self-Care, Travel, Food, Fitness.
            """

            ctx.data["tweet_analyzer_agent"] = self.create_agent(ctx, [categorize_tweets], system_prompt)

        interests = ctx.data["tweet_analyzer_agent"].chat(f"Analyze these tweets: {ev.tweets}")
        self.log_print(f"Interests identified: {str(interests)}")
        return InterestMapperEvent(interests=str(interests))

    @step(pass_context=True)
    async def interest_mapper(self, ctx: Context, ev: InterestMapperEvent) -> GiftIdeaGeneratorEvent:
        self.log_print("Step: Interest Mapper")
        if "interest_mapper_agent" not in ctx.data:
            def map_interests_to_gift_categories(interests: str) -> str:
                prompt = f"""For each of the following interest categories, suggest potential gift categories.
                If the interests are unclear, use these default gift categories: 
                'specialty dark chocolate','premium coffee','charcuterie board items','perishable boutique pantry items'.
                Provide a comma-separated list of at least 10 gift categories:

                Interest categories:
                {interests}

                Gift categories:"""
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip()

            system_prompt = """
                You are an AI assistant specializing in mapping interest categories to potential gift categories. 
                Your task is to generate a diverse and relevant list of at least 10 gift categories based on given interests.
                If the interests are unclear or insufficient, use these default gift categories: 
                Charcuterie, fruit preserves, fancy olive oil, specialty nut butters.
                Ensure each gift category is specific enough to be useful for gift searching, but broad enough to encompass multiple gift options.
            """

            ctx.data["interest_mapper_agent"] = self.create_agent(ctx, [map_interests_to_gift_categories], system_prompt)

        gift_categories = ctx.data["interest_mapper_agent"].chat(f"Map these interests to gift categories: {ev.interests}")
        self.log_print(f"Gift Categories: {str(gift_categories)}")
        return GiftIdeaGeneratorEvent(gift_categories=str(gift_categories))

    @step(pass_context=True)
    async def gift_idea_generator(self, ctx: Context, ev: GiftIdeaGeneratorEvent) -> MediationEvent:
        self.log_print("Step: Gift Idea Generator")
        try:
            if "gift_idea_generator_agent" not in ctx.data:
                def generate_specific_gift_ideas(gift_categories: str, interests: str, tweets: List[str]) -> str:
                    prompt = f"""Based on the following user-specific information:

                    Interests: {interests}
                    Tweets: {tweets}
                    Gift Categories: {gift_categories}

                    Generate unique and specific gift ideas under ${self.price_ceiling}. 
                    Focus on items that are:
                    1. Directly related to the user's interests and gift categories
                    2. Unique and not commonly found in regular stores
                    3. Specific to the person's interests, avoiding generic items
                    4. Preferably from local artisans, small businesses, or specialty shops
                    5. Include a mix of physical items and experiences
                    6. Aim for a total of 10 gift ideas across all categories

                    Present your suggestions as a Python dictionary where keys are categories and values are lists of gift ideas.
                    Each gift idea should be a string in the format "Category: Gift Idea".
                    Ensure that each gift idea is tailored to the user's specific interests and not generic.
                    Do not use any default suggestions.

                    Gift Ideas:"""
                    response = ctx.data["llm"].complete(prompt)
                    return str(response).strip()

                system_prompt = """
                    You are an AI assistant specialized in generating unique and thoughtful gift ideas based on specific user information.
                    Your task is to suggest gift items that are tailored to the user's interests, tweets, and identified gift categories.
                    Focus on items that are unique, personal, and directly related to the user's preferences.
                    Avoid any generic or default suggestions.
                    Provide your suggestions as a Python dictionary where keys are categories and values are lists of gift ideas.
                """

                ctx.data["gift_idea_generator_agent"] = self.create_agent(ctx, [generate_specific_gift_ideas], system_prompt)

            # Retrieve user-specific information from previous steps
            interests = ctx.data.get("interests", "")
            tweets = ctx.data.get("tweets", [])

            gift_ideas_str = ctx.data["gift_idea_generator_agent"].chat(
                f"Generate gift ideas for these categories: {ev.gift_categories}, "
                f"with these interests: {interests}, and these tweets: {tweets}"
            )

            self.log_print(f"Raw Gift Ideas Output: {gift_ideas_str}")
            
            gift_ideas_list = []
            try:
                # Try to parse as a Python dictionary
                gift_ideas_dict = ast.literal_eval(str(gift_ideas_str))
                if isinstance(gift_ideas_dict, dict):
                    for category, items in gift_ideas_dict.items():
                        for item in items:
                            gift_ideas_list.append(f"{category}: {item}")
            except (SyntaxError, ValueError):
                # If parsing fails, extract ideas manually
                self.log_print("Parsing as dictionary failed. Extracting ideas manually.")
                lines = str(gift_ideas_str).split('\n')
                current_category = ""
                for line in lines:
                    if line.strip().endswith(':'):
                        current_category = line.strip()[:-1]
                    elif line.strip().startswith('-'):
                        item = line.strip()[1:].strip()
                        gift_ideas_list.append(f"{current_category}: {item}")

            # If we still don't have any gift ideas, use fallback options
            if not gift_ideas_list:
                self.log_print("No gift ideas extracted. Using fallback options.")
                fallback_ideas = [
                    "Technology: Portable smartphone projector",
                    "Self-Care: Organic facial serum",
                    "Entertainment: Independent cinema movie tickets",
                    "Music: Vintage vinyl record",
                    "Photography: Mini tabletop tripod for smartphones"
                ]
                gift_ideas_list.extend(fallback_ideas)

            self.log_print(f"Processed Gift Ideas: {str(gift_ideas_list)}")
            return MediationEvent(gift_ideas=gift_ideas_list)
        except Exception as e:
            self.log_print(f"Error in gift_idea_generator: {str(e)}")
            fallback_ideas = [
                "Technology: High-quality charger cable",
                "Food: perishable boutique pantry items",
                "Self-Care: Aromatherapy diffuser",
                "Entertainment: Streaming service gift card",
                "Fitness: Compact resistance bands set"
            ]
            return MediationEvent(gift_ideas=fallback_ideas)

    def initialize_debate_agents(self, ctx: Context):
        if "gift_con_agent" not in ctx.data:
            def argue_against_gift(gift_idea: str) -> str:
                prompt = f"""Argue against the following gift idea as a Christmas gift under ${self.price_ceiling} in 300 characters or less. 
                Consider factors like potential misalignment with recipient's interests, lack of practicality, inappropriateness, or reasons the recipient might not appreciate the gift.

                Gift idea: {gift_idea}

                Provide a concise argument against this gift:"""
                return ctx.data["llm"].complete(prompt)

            con_system_prompt = """
                You are an AI assistant that argues against gift ideas. Your role is to:
                1. Present strong arguments opposing the given gift idea.
                2. Focus on potential drawbacks or limitations of the gift.
                3. Provide specific reasons why the recipient might not appreciate the gift.
                4. Keep your argument concise and persuasive, within 300 characters.
            """

            ctx.data["gift_con_agent"] = self.create_agent(ctx, [argue_against_gift], con_system_prompt)

        if "gift_pro_agent" not in ctx.data:
            def argue_for_gift(gift_idea: str, previous_argument: str) -> str:
                prompt = f"""Argue in favor of the following gift idea as a Christmas gift under ${self.price_ceiling} in 300 characters or less. 
                Consider factors like alignment with recipient's interests, practicality, appropriateness, and reasons the recipient might appreciate the gift.
                Address the previous argument against the gift.

                Gift idea: {gift_idea}
                Previous argument against: {previous_argument}

                Provide a concise argument in favor of this gift:"""
                return ctx.data["llm"].complete(prompt)

            pro_system_prompt = """
                You are an AI assistant that argues in favor of gift ideas. Your role is to:
                1. Present strong arguments supporting the given gift idea based on the user's interests.
                2. Address and counter the previous argument against the gift.
                3. Focus on the positive aspects and potential benefits of the gift.
                4. Keep your argument concise and persuasive, within 300 characters.
            """

            ctx.data["gift_pro_agent"] = self.create_agent(ctx, [argue_for_gift], pro_system_prompt)

    @step(pass_context=True)
    async def mediation_agent(self, ctx: Context, ev: MediationEvent) -> GiftDebaterEvent:
        self.log_print("Step: Mediation Agent")
        if not ev.gift_ideas:
            self.log_print("No gift ideas to debate. Providing fallback ideas.")
            fallback_ideas = ["high-quality charger cable", "perishable boutique pantry items", "Gourmet Chocolate", "Portable Charger", "Cozy Socks"]
            debates = {gift: {"pro": "Versatile gift", "con": "May not match specific interests"} for gift in fallback_ideas}
            return GiftDebaterEvent(gift_ideas=fallback_ideas, debates=debates)
        
        
        try:
            self.initialize_debate_agents(ctx)

            debates = {gift: {"pro": "", "con": ""} for gift in ev.gift_ideas}

            for i, gift in enumerate(ev.gift_ideas):
                self.log_print(f"Processing gift {i+1}/{len(ev.gift_ideas)}: {gift}")
                
                try:
                    # Argue against
                    con_response = ctx.data["gift_con_agent"].chat(f"Argue against this gift idea: {gift}")
                    con_argument = con_response.response if hasattr(con_response, 'response') else str(con_response)
                    debates[gift]["con"] = con_argument

                    # Argue for
                    pro_response = ctx.data["gift_pro_agent"].chat(f"Argue for this gift idea, considering: {con_argument[:300]}")
                    pro_argument = pro_response.response if hasattr(pro_response, 'response') else str(pro_response)
                    debates[gift]["pro"] = pro_argument
                
                except Exception as e:
                    self.log_print(f"Error processing gift '{gift}': {str(e)}")
                    debates[gift]["con"] = "Error generating argument"
                    debates[gift]["pro"] = "Error generating argument"

            self.log_print(f"Gift Debates: {str(debates)}")
            return GiftDebaterEvent(gift_ideas=ev.gift_ideas, debates=debates)
        
        except Exception as e:
            self.log_print(f"Error in mediation_agent: {str(e)}")
            traceback.print_exc()
            raise

    @step(pass_context=True)
    async def gift_debater(self, ctx: Context, ev: GiftDebaterEvent) -> GiftReasonerEvent:
        self.log_print("Step: Gift Debater")
        
        self.initialize_debate_agents(ctx)

        extended_debates = {}
        for gift_idea in ev.gift_ideas:
            extended_debates[gift_idea] = []
            # Initial arguments from mediation_agent
            extended_debates[gift_idea].append(f"Con: {ev.debates[gift_idea]['con']}")
            extended_debates[gift_idea].append(f"Pro: {ev.debates[gift_idea]['pro']}")

            # 3 rounds of back-and-forth arguments
            for i in range(3):
                pro_response = ctx.data["gift_pro_agent"].chat(f"Argue for this gift idea: {gift_idea}, considering: {ev.debates[gift_idea]['con']}")
                pro_argument = pro_response.response if hasattr(pro_response, 'response') else str(pro_response)
                extended_debates[gift_idea].append(f"Pro: {pro_argument[:300]}")
                
                if i < 2:  # Only do con argument for the first two rounds
                    con_response = ctx.data["gift_con_agent"].chat(f"Counter this argument: {pro_argument[:300]}")
                    con_argument = con_response.response if hasattr(con_response, 'response') else str(con_response)
                    extended_debates[gift_idea].append(f"Con: {con_argument[:300]}")

            # 3 rounds of one-sentence arguments
            for _ in range(3):
                pro_response = ctx.data["gift_pro_agent"].chat(f"Give a one-sentence argument for {gift_idea}")
                pro_argument = pro_response.response if hasattr(pro_response, 'response') else str(pro_response)
                extended_debates[gift_idea].append(f"Pro: {pro_argument[:300]}")
                
                con_response = ctx.data["gift_con_agent"].chat(f"Give a one-sentence argument against {gift_idea}")
                con_argument = con_response.response if hasattr(con_response, 'response') else str(con_response)
                extended_debates[gift_idea].append(f"Con: {con_argument[:300]}")

        self.log_print(f"Extended Gift Debates: {str(extended_debates)}")
        return GiftReasonerEvent(debates=extended_debates)

    @step(pass_context=True)
    async def gift_reasoner(self, ctx: Context, ev: GiftDebaterEvent) -> GiftReasonerEvent:
        self.log_print("Step: Gift Reasoner")
        if "gift_reasoner_agent" not in ctx.data:
            def reason_over_debates(debates: str) -> str:
                prompt = f"""Given the following debates about gift ideas, provide a final reasoned selection of the top 5 gift ideas. 
                Consider factors such as uniqueness, practicality, and how well they match the recipient's interests. 
                Present your selection as a Python list of strings, where each string is in the format "Gift Idea: Reasoning".

                Debates:
                {debates}

                Final Selection:"""
                return ctx.data["llm"].complete(prompt)

            system_prompt = """
                You are an AI assistant specialized in analyzing debates about gift ideas and making final selections.
                Your task is to consider various factors and provide a reasoned selection of the top 5 gift ideas.
                Present your selection as a Python list of strings, where each string includes both the gift idea and the reasoning behind it.
            """

            ctx.data["gift_reasoner_agent"] = self.create_agent(ctx, [reason_over_debates], system_prompt)

        max_retries = 3
        retry_delay = 5  # seconds

        for attempt in range(max_retries):
            try:
                final_gifts = ctx.data["gift_reasoner_agent"].chat(f"Reason over these debates: {ev.debates}")
                self.log_print(f"Final Gift Selection: {final_gifts}")
                
                # Extract the response from AgentChatResponse
                final_gifts_list = ast.literal_eval(final_gifts.response)
                
                # Create a dictionary with gift ideas as keys and reasons as values
                reasoned_gifts = {gift.split(":")[0].strip(): [gift.split(":", 1)[1].strip()] for gift in final_gifts_list}
                
                return GiftReasonerEvent(gift_ideas=reasoned_gifts)
            except Exception as e:
                self.log_print(f"Error in gift_reasoner (attempt {attempt + 1}/{max_retries}): {str(e)}")
                if attempt < max_retries - 1:
                    self.log_print(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    self.log_print("Max retries reached. Using fallback method.")
                    fallback_gifts = self.fallback_gift_selection(ev.debates)
                    return GiftReasonerEvent(gift_ideas=fallback_gifts)

    def fallback_gift_selection(self, debates: Dict[str, Dict[str, str]]) -> Dict[str, List[str]]:
        # Simple fallback method to extract gift ideas from debates
        fallback_gifts = {}
        for gift, debate in debates.items():
            pro_argument = debate.get('pro', 'No pro argument available')
            fallback_gifts[gift] = [f"Selected as a fallback option. Pro argument: {pro_argument[:100]}..."]
        
        # If we have more than 5 gifts, randomly select 5
        if len(fallback_gifts) > 5:
            selected_gifts = random.sample(list(fallback_gifts.keys()), 5)
            fallback_gifts = {gift: fallback_gifts[gift] for gift in selected_gifts}
        
        return fallback_gifts
    
    @step(pass_context=True)
    async def amazon_keyword_generator(self, ctx: Context, ev: GiftReasonerEvent) -> AmazonKeywordGeneratorEvent:
        if "amazon_keyword_generator_agent" not in ctx.data:
            def generate_keywords(gift_ideas: List[str]) -> List[str]:
                prompt = f"""Based on the following gift ideas, generate Amazon search keywords. 
                Each keyword should be a short phrase suitable for searching on Amazon, 
                and should include "under ${self.price_ceiling}" or a similar price qualifier.

                Gift ideas:
                {', '.join(gift_ideas)}

                Provide a Python list of 3 search keywords:"""
                response = ctx.data["llm"].complete(prompt)
                return eval(str(response).strip())

            system_prompt = """
                You are an AI assistant that generates Amazon search keywords based on gift ideas.
                Your task is to provide a list of 3 search keywords suitable for Amazon, including a price qualifier.
            """

            ctx.data["amazon_keyword_generator_agent"] = self.create_agent(ctx, [generate_keywords], system_prompt)

        # Convert the gift_ideas dictionary to a list of strings
        gift_ideas_list = [f"{gift}: {reasons[0]}" for gift, reasons in ev.gift_ideas.items()]

        amazon_keywords = ctx.data["amazon_keyword_generator_agent"].chat(
            f"Generate keywords for these gift ideas: {gift_ideas_list}"
        )
                
        # Extract the content from the AgentChatResponse
        response_text = amazon_keywords.response.strip()
        
        # Parse the keywords from the response text
        keywords_list = []
        for line in response_text.split('\n'):
            if line.strip().startswith(('- ', '• ', '* ', '1. ', '2. ', '3. ', '4. ', '5. ', '6. ', ',','.')):
                keywords_list.append(line.strip().split(' ', 1)[1])
        
        # Ensure we have at least one keyword
        if not keywords_list:
            self.log_print("Failed to generate valid keywords. Using fallback keyword.")
            keywords_list = [f"Gift under ${self.price_ceiling}"]  # Fallback keyword

        return AmazonKeywordGeneratorEvent(gift_ideas=gift_ideas_list, amazon_keywords=keywords_list)
    
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
    async def amazon_product_link_generator(self, ctx: Context, ev: AmazonProductLinkEvent) -> ProductLinkEvent:
        self.log_print(f"Generating product link for keyword: {ev.keyword}")
        
        product_link = []
        link = self.extract_amazon_product_links(ev.keyword)
        product_link.extend(link)
        
        self.log_print("\n--- Amazon Product Links ---")
        self.log_print(product_link)
        self.log_print("----------------------------\n")
        
        try:
            if not product_link:
                raise ValueError("No product data returned")
            
            product_link = product_link[0]
            
            # Safely extract values with default fallbacks
            title = product_link.get('title', 'No title available')
            price = product_link.get('price', {})
            if isinstance(price, dict):
                price_value = price.get('value')
                if price_value is not None:
                    try:
                        price_value = float(price_value)
                    except ValueError:
                        price_value = None
            else:
                price_value = None
            
            rating = product_link.get('stars')
            if rating is not None:
                try:
                    rating = float(rating)
                except ValueError:
                    rating = None
            
            image = product_link.get('thumbnailImage') or product_link.get('thumbnail', '')
            url = product_link.get('url', '')
            self.log_print(f"Creating ProductLinkEvent with: title={title}, price={price_value}, rating={rating}, image={image}, url={url}")

            return ProductLinkEvent(
                product_title=title,
                product_price=price_value,
                product_rating=rating,
                product_image=image,
                product_links=url
            )
        except Exception as e:
            self.log_print(f"An error occurred while processing product link: {str(e)}")
            traceback.print_exc()
            return ProductLinkEvent(
                product_title="No product found",
                product_price=None,
                product_rating=None,
                product_image="",
                product_links=""
            )

# Remove the draw_all_possible_flows call from here
def create_agent(ctx: Context, tools: List[callable], system_prompt: str):
    function_tools = [FunctionTool.from_defaults(fn=tool) for tool in tools]
    agent_worker = FunctionCallingAgentWorker.from_tools(
        tools=function_tools,
        llm=ctx.data["llm"],
        allow_parallel_tool_calls=False,
        system_prompt=system_prompt
    )
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
        log_print(result)
    except Exception as e:
        log_print(f"An error occurred: {str(e)}")
        traceback.print_exc(file=sys.stdout)
    finally:
        log_print(f"Log saved to: {log_path}")

if __name__ == "__main__":
    asyncio.run(main())