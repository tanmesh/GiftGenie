import os
import asyncio
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

class GiftSuggestionWorkflow(Workflow):
    def __init__(self, price_ceiling: float, log_print_func, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price_ceiling = price_ceiling
        self.log_print = log_print_func

    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: StartEvent) -> TweetAnalyzerEvent:
        self.log_print("Step: Get Tweets and Compile Text")
        ctx.data["llm"] = OpenAI(model="gpt-4", temperature=0.4)
        
        twitter_handle = ctx.data.get("twitter_handle", "")
        additional_text = ctx.data.get("additional_text", "")
        
        tweets = []
        
        # Generate tweets based on Twitter handle if provided
        if twitter_handle:
            tweets = [f"Tweet from {twitter_handle}: This is a dummy tweet {i}" for i in range(1, 6)]
        
        # If no tweets from Twitter handle, use default tweets
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

        interests = ctx.data["tweet_analyzer_agent"].chat(f"Analyze these tweets: {ev.tweets}")
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

        gift_categories = ctx.data["interest_mapper_agent"].chat(f"Map these interests to gift categories: {ev.interests}")
        print("\n--- Gift Categories ---")
        print(str(gift_categories))
        print("--------------------\n")
        self.log_print(f"Gift Categories: {str(gift_categories)}")
        return GiftIdeaGeneratorEvent(gift_categories=str(gift_categories))

    @step(pass_context=True)
    async def gift_idea_generator(self, ctx: Context, ev: GiftIdeaGeneratorEvent) -> GiftDebaterEvent:
        if "gift_idea_generator_agent" not in ctx.data:
            def generate_affordable_gift_ideas(gift_categories: str) -> str:
                prompt = f"""For each of the following gift categories, suggest gift ideas under ${self.price_ceiling}. Always recommend 10 items in total, including perishable boutique pantry items like pumpkin seed butter or fancy trail mix. Provide a comma-separated list of 10 gift ideas:

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

        gift_ideas = ctx.data["gift_idea_generator_agent"].chat(f"Generate gift ideas for these categories: {ev.gift_categories}")
        print("\n--- Gift Ideas ---")
        print(str(gift_ideas))
        print("--------------------\n")
        self.log_print(f"Gift Ideas: {str(gift_ideas)}")
        return GiftDebaterEvent(gift_ideas=str(gift_ideas))


    @step(pass_context=True)
    async def gift_debater(self, ctx: Context, ev: GiftDebaterEvent) -> GiftReasonerEvent:
        if "gift_debater_agent" not in ctx.data:
            def debate_gift_ideas(gift_ideas: str) -> str:
                prompt = f"""Debate the following gift ideas as Christmas gifts under $40. Consider if the person might not like the gift, 
                whether it's perishable, and if it's age or demographically appropriate. Consider especially How well does this align with
                the recipient's interest categories?
                Practicality: is this something the recipient could use regularly or would find particularly useful?
                Appropriateness: Is the item suitable for a gift appropriate to the recipient's age, gender, lifestyle and demographic?
                Are there any reasons the recipient might not appreciate this gift?
                
                Provide your debate in a structured format as a transcript where the one llm is for the item, and the other llm is against the item as a gift:

                Gift ideas:
                {gift_ideas}

                Debate:"""
                
                llm1_response = ctx.data["llm"].complete(prompt + "\nLLM1 (For):")
                llm2_response = ctx.data["llm"].complete(prompt + "\nLLM2 (Against):")
                
                return f"LLM1 (For): {str(llm1_response)}\n\nLLM2 (Against): {str(llm2_response)}"

            system_prompt = """
                You are an AI assistant that debates gift ideas.
                Your task is to provide arguments for and against each gift idea, considering factors like personal preference, perishability, and appropriateness.
            """

            ctx.data["gift_debater_agent"] = create_agent(ctx, [debate_gift_ideas], system_prompt)

        debates = ctx.data["gift_debater_agent"].chat(f"Debate these gift ideas: {ev.gift_ideas}")
        
        # Print the debates for the user to see
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

        final_gifts = ctx.data["gift_reasoner_agent"].chat(f"Reason over these debates: {ev.debates}")
        
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
        print("Step: Amazon Keyword Generator")
        if "amazon_keyword_generator_agent" not in ctx.data:
            def generate_keywords(gift_ideas: List[str]) -> List[str]:
                prompt = f"""Based on the following gift ideas, generate Amazon search keywords. 
                Each keyword should be a short phrase suitable for searching on Amazon, 
                and should include "under ${self.price_ceiling}" as the price qualifier.

                Gift ideas:
                {', '.join(gift_ideas)}

                Provide exactly 3 search keywords in the format of a Python list of strings. 
                For example: ["smart home devices under ${self.price_ceiling}", "cleaning gadgets under ${self.price_ceiling}", "kitchen tools under ${self.price_ceiling}"]

                Your response:"""
                
                response = ctx.data["llm"].complete(prompt)
                
                try:
                    keywords = ast.literal_eval(response.strip())
                    if isinstance(keywords, list) and all(isinstance(item, str) and f"under ${self.price_ceiling}" in item for item in keywords):
                        return keywords[:3]
                    else:
                        raise ValueError("Response is not a valid list of strings with correct price ceiling")
                except:
                    keywords = response.strip().replace("[", "").replace("]", "").split(",")
                    return [f"{kw.strip().strip('\"\'').split(' under ')[0]} under ${self.price_ceiling}" for kw in keywords[:3]]

            system_prompt = f"""
                You are an AI assistant that generates Amazon search keywords based on gift ideas.
                Your task is to provide a list of exactly 3 search keywords suitable for Amazon, including the price qualifier "under ${self.price_ceiling}".
                Always format your response as a valid Python list of strings.
                For example: ["smart home devices under ${self.price_ceiling}", "cleaning gadgets under ${self.price_ceiling}", "kitchen tools under ${self.price_ceiling}"]
            """

            ctx.data["amazon_keyword_generator_agent"] = create_agent(ctx, [generate_keywords], system_prompt)

        amazon_keywords = ctx.data["amazon_keyword_generator_agent"].chat(f"Generate keywords for these gift ideas: {ev.gift_ideas}")
        print(f"Amazon Search Keywords: {amazon_keywords}")
        self.log_print(f"Amazon Search Keywords: {str(amazon_keywords)}")
        return StopEvent()

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