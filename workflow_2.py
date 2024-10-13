import os
from dotenv import load_dotenv
from typing import List, Optional
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
    @step(pass_context=True)
    async def initialize(self, ctx: Context, ev: StartEvent) -> TweetAnalyzerEvent:
        ctx.data["llm"] = OpenAI(model="gpt-4", temperature=0.4)
        tweets = [
            "Just finished a great workout at the gym!",
            "Can't wait for my camping trip next weekend. Need to get some gear!",
            "Loving my new smartphone. The camera is amazing!",
            "Trying to eat healthier. Any good cookbook recommendations?",
            "Working on a new coding project. Python is so fun!"
        ]
        return TweetAnalyzerEvent(tweets=tweets)

    @step(pass_context=True)
    async def tweet_analyzer(self, ctx: Context, ev: TweetAnalyzerEvent) -> InterestMapperEvent:
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
                You are an AI assistant that maps interest categories to potential gift categories.
                Your task is to provide a comma-separated list of gift categories based on the given interests.
            """

            ctx.data["interest_mapper_agent"] = create_agent(ctx, [map_interests_to_gift_categories], system_prompt)

        gift_categories = ctx.data["interest_mapper_agent"].chat(f"Map these interests to gift categories: {ev.interests}")
        return GiftIdeaGeneratorEvent(gift_categories=str(gift_categories))

    @step(pass_context=True)
    async def gift_idea_generator(self, ctx: Context, ev: GiftIdeaGeneratorEvent) -> GiftDebaterEvent:
        if "gift_idea_generator_agent" not in ctx.data:
            def generate_affordable_gift_ideas(gift_categories: str) -> str:
                prompt = f"""For each of the following gift categories, suggest gift ideas under $40. Always recommend 10 items in total, including perishable boutique pantry items like pumpkin seed butter or fancy trail mix. Provide a comma-separated list of 10 gift ideas:

                Gift categories:
                {gift_categories}"""
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip()

            system_prompt = """
                You are an AI assistant that generates affordable gift ideas based on gift categories.
                Your task is to provide a comma-separated list of 10 gift ideas under $40, including some perishable boutique pantry items.
            """

            ctx.data["gift_idea_generator_agent"] = create_agent(ctx, [generate_affordable_gift_ideas], system_prompt)

        gift_ideas = ctx.data["gift_idea_generator_agent"].chat(f"Generate gift ideas for these categories: {ev.gift_categories}")
        return GiftDebaterEvent(gift_ideas=str(gift_ideas))

    @step(pass_context=True)
    async def gift_debater(self, ctx: Context, ev: GiftDebaterEvent) -> GiftReasonerEvent:
        if "gift_debater_agent" not in ctx.data:
            def debate_gift_ideas(gift_ideas: str) -> str:
                prompt = f"""Debate the following gift ideas as Christmas gifts under $40. Consider if the person might not like the gift, whether it's perishable, and if it's age or demographically appropriate. Provide your debate in a structured format:

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

        return GiftReasonerEvent(debates=str(debates))

    @step(pass_context=True)
    async def gift_reasoner(self, ctx: Context, ev: GiftReasonerEvent) -> AmazonKeywordGeneratorEvent:
        if "gift_reasoner_agent" not in ctx.data:
            def reason_over_debates(debates: str) -> List[str]:
                prompt = f"""Based on the following debates, reason over the arguments and select the 3 best gift ideas. Provide a final take on why these 3 were chosen:

                Debates:
                {debates}

                Final selection (list the 3 chosen gifts and reasons):"""
                
                response = ctx.data["llm"].complete(prompt)
                return str(response).strip().split('\n')

            system_prompt = """
                You are an AI assistant that reasons over gift idea debates.
                Your task is to select the 3 best gift ideas based on the debates and provide reasons for your choices.
            """

            ctx.data["gift_reasoner_agent"] = create_agent(ctx, [reason_over_debates], system_prompt)

        final_gifts = ctx.data["gift_reasoner_agent"].chat(f"Reason over these debates: {ev.debates}")
        
        # Print the final gift selections for the user to see
        print("\n--- Final Gift Selections ---")
        print(str(final_gifts))
        print("------------------------------\n")

        # Convert the AgentChatResponse to a list of strings
        gift_list = str(final_gifts).strip().split('\n')
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

            ctx.data["amazon_keyword_generator_agent"] = create_agent(ctx, [generate_keywords], system_prompt)

        amazon_keywords = ctx.data["amazon_keyword_generator_agent"].chat(f"Generate keywords for these gift ideas: {ev.gift_ideas}")
        print("Amazon Search Keywords:", amazon_keywords)
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
    workflow = GiftSuggestionWorkflow(timeout=1200, verbose=True)
    result = await workflow.run()
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())