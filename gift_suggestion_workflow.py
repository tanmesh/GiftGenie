from typing import List, Dict
import re
from llama_index.llms.openai import OpenAI
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
import traceback
from llama_index.core.workflow import draw_all_possible_flows
from searchx import search_tweets
from typing import List, Dict
from llama_index.core.workflow import Event
import sys
import json
from typing import Union


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
    debates: Dict[str, List[str]]

class AmazonKeywordGeneratorEvent(Event):
    gift_ideas: List[str]
    amazon_keywords: List[str] = []

class AmazonKeywordEvent(Event):
    amazon_keywords: List[str]

class AmazonProductLinkEvent(Event):
    keyword: str

class ProductLinkEvent(Event):
    product_title: str
    product_price: float
    product_rating: float
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
                If you can't determine specific interests, use these default categories: Technology, Books, Travel, Food, Fitness.
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
                Technology, Books, Travel, Food, Fitness.
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
                Tech Gadgets, Bestselling Books, Travel Accessories, Gourmet Food Items, Fitness Equipment.
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
                Tech Gadgets, Bestselling Books, Travel Accessories, Gourmet Food Items, Fitness Equipment.
                Ensure each gift category is specific enough to be useful for gift searching, but broad enough to encompass multiple gift options.
            """

            ctx.data["interest_mapper_agent"] = self.create_agent(ctx, [map_interests_to_gift_categories], system_prompt)

        gift_categories = ctx.data["interest_mapper_agent"].chat(f"Map these interests to gift categories: {ev.interests}")
        self.log_print(f"Gift Categories: {str(gift_categories)}")
        return GiftIdeaGeneratorEvent(gift_categories=str(gift_categories))

    @step(pass_context=True)
    async def gift_idea_generator(self, ctx: Context, ev: GiftIdeaGeneratorEvent) -> MediationEvent:
        self.log_print("Step: Gift Idea Generator")
        if "gift_idea_generator_agent" not in ctx.data:
            def generate_affordable_gift_ideas(gift_categories: str) -> str:
                prompt = f"""For each of the following gift categories, suggest gift ideas under ${self.price_ceiling}. 
                Always recommend only 2 items per category which may include perishable boutique pantry items like pumpkin seed butter or fancy trail mix. 
                If the gift categories are unclear, use these default ideas: 
                Wireless earbuds, Bestselling novel, Travel neck pillow, Gourmet coffee sampler, Resistance bands set.
                Provide a Python list of specific gift ideas. For example:
                ['Wireless earbuds', 'Bestselling novel']

                Gift categories:
                {gift_categories}"""
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip()

            system_prompt = """
                You are an AI assistant specialized in generating affordable gift ideas based on given categories.
                Your task is to suggest 2 specific gift items for each category, ensuring they are under the specified price ceiling.
                Provide your suggestions as a Python list of strings.
            """

            ctx.data["gift_idea_generator_agent"] = self.create_agent(ctx, [generate_affordable_gift_ideas], system_prompt)

        gift_ideas_str = ctx.data["gift_idea_generator_agent"].chat(f"Generate gift ideas for these categories: {ev.gift_categories}")

        self.log_print(f"Raw Gift Ideas Output: {gift_ideas_str}")
        
        try:
            gift_ideas_list = ast.literal_eval(str(gift_ideas_str))
            if not isinstance(gift_ideas_list, list):
                raise ValueError("Result is not a list")
        except (SyntaxError, ValueError) as e:
            self.log_print(f"Error parsing gift ideas: {e}")
            self.log_print(f"Raw output: {gift_ideas_str}")
            # Extract gift ideas from the raw output
            gift_ideas_list = [item.strip() for item in re.findall(r"'([^']*)'", str(gift_ideas_str))]
            if not gift_ideas_list:
                gift_ideas_list = ["Wireless earbuds", "Bestselling novel"]

        # Limit the list to 5 items
        gift_ideas_list = gift_ideas_list[:5]

        self.log_print(f"Processed Gift Ideas: {str(gift_ideas_list)}")
        return MediationEvent(gift_ideas=gift_ideas_list)

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
                1. Present strong arguments supporting the given gift idea.
                2. Address and counter the previous argument against the gift.
                3. Focus on the positive aspects and potential benefits of the gift.
                4. Keep your argument concise and persuasive, within 300 characters.
            """

            ctx.data["gift_pro_agent"] = self.create_agent(ctx, [argue_for_gift], pro_system_prompt)

    @step(pass_context=True)
    async def mediation_agent(self, ctx: Context, ev: MediationEvent) -> GiftDebaterEvent:
        self.log_print("Step: Mediation Agent")
        
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
    async def gift_reasoner(self, ctx: Context, ev: GiftReasonerEvent) -> MediationEvent:
        self.log_print("Step: Gift Reasoner")
        if "gift_reasoner_agent" not in ctx.data:
            def reason_over_debates(debates: Dict[str, List[str]]) -> List[str]:
                prompt = f"""Based on the following debates, reason over the arguments and select the 3 best specific gift items. 
                Provide a final take on why these 3 were chosen. Pay special attention to the pro arguments, as they were the last to argue in each debate:

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
                different aspects of the recipient's interests or needs. Pay special attention to the pro arguments,
                as they were the last to argue in each debate.
            """

            ctx.data["gift_reasoner_agent"] = self.create_agent(ctx, [reason_over_debates], system_prompt)

        final_gifts = ctx.data["gift_reasoner_agent"].chat(f"Reason over these debates: {ev.debates}")
        
        gift_list = [line for line in str(final_gifts).strip().split('\n') if line.strip()]
        self.log_print(f"Final Gift Selections: {str(gift_list)}")
        return MediationEvent(gift_ideas=gift_list)
    
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

        amazon_keywords = ctx.data["amazon_keyword_generator_agent"].chat(
            f"Generate keywords for these gift ideas: {ev.gift_ideas}"
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
            self.log_print("Failed to generate valid keywords. Using fallback keyword.")
            keywords_list = [f"Gift under ${self.price_ceiling}"]  # Fallback keyword

        return AmazonKeywordGeneratorEvent(gift_ideas=ev.gift_ideas, amazon_keywords=keywords_list)

    @step(pass_context=True)
    async def amazon_product_link_generator(self, ctx: Context, ev: AmazonProductLinkEvent) -> ProductLinkEvent:
        self.log_print(f"Generating product link for keyword: {ev.keyword}")
        
        if "amazon_product_link_generator_agent" not in ctx.data:
            def generate_product_link(keyword: str) -> str:
                prompt = f"""Generate a simulated Amazon product based on the following search keyword: {keyword}
                Provide the following details:
                - Product title (max 50 characters)
                - Price (as a float, under {self.price_ceiling})
                - Rating (as a float between 1 and 5)
                - Image URL (use 'https://example.com/sample-image.jpg')
                - Product URL (use 'https://www.amazon.com/s?k={keyword.replace(' ', '+')}')

                Format your response as follows:
                Title: [Product Title]
                Price: [Price]
                Rating: [Rating]
                Image: [Image URL]
                URL: [Product URL]
                """
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip()

            system_prompt = """
                You are an AI assistant that generates simulated Amazon product listings based on search keywords.
                Your task is to provide realistic product details including title, price, rating, and URLs.
            """

            ctx.data["amazon_product_link_generator_agent"] = self.create_agent(ctx, [generate_product_link], system_prompt)

        product_data = ctx.data["amazon_product_link_generator_agent"].chat(f"Generate a product link for: {ev.keyword}")
        
        # Parse the response
        response_text = product_data.response.strip()
        product_dict = {}
        for line in response_text.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                product_dict[key.strip().lower()] = value.strip()

        # Extract values and provide defaults if not found
        title = product_dict.get('title', 'No title available')
        price = float(re.search(r'\d+(\.\d+)?', product_dict.get('price', '0')).group()) if 'price' in product_dict else 0.0
        rating = float(re.search(r'\d+(\.\d+)?', product_dict.get('rating', '0')).group()) if 'rating' in product_dict else 0.0
        image = product_dict.get('image', 'https://example.com/sample-image.jpg')
        url = product_dict.get('url', f'https://www.amazon.com/s?k={ev.keyword.replace(" ", "+")}')

        return ProductLinkEvent(
            product_title=title,
            product_price=price,
            product_rating=rating,
            product_image=image,
            product_links=url
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