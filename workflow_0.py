import os
from dotenv import load_dotenv
from llama_index.core.workflow import (
    Event,
    StartEvent,
    StopEvent,
    Workflow,
    step,
)
from llama_index.llms.openai import OpenAI

# Load environment variables from .env file
load_dotenv()

class JokeEvent(Event):
    joke: str

class JokeFlow(Workflow):
    llm = OpenAI()

    @step
    async def generate_joke(self, ev: StartEvent) -> JokeEvent:
        topic = ev.topic
        prompt = f"Write your best joke about {topic}."
        try:
            response = await self.llm.acomplete(prompt)
            return JokeEvent(joke=str(response))
        except Exception as e:
            print(f"Error generating joke: {e}")
            return JokeEvent(joke="Error generating joke")

    @step
    async def critique_joke(self, ev: JokeEvent) -> StopEvent:
        joke = ev.joke
        prompt = f"Give a thorough analysis and critique of the following joke: {joke}"
        try:
            response = await self.llm.acomplete(prompt)
            return StopEvent(result=str(response))
        except Exception as e:
            print(f"Error critiquing joke: {e}")
            return StopEvent(result="Error critiquing joke")

async def main():
    if "OPENAI_API_KEY" not in os.environ:
        raise ValueError("Please set the OPENAI_API_KEY environment variable")
    
    w = JokeFlow(timeout=60, verbose=False)
    result = await w.run(topic="pirates")
    print(str(result))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())