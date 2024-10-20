import asyncio
from gift_suggestion_workflow import GiftSuggestionWorkflow
from llama_index.utils.workflow import draw_all_possible_flows

async def generate_graph():
    # Generate the graph
    draw_all_possible_flows(GiftSuggestionWorkflow, filename="gift_suggestion_workflow.html")
    print("Workflow graph has been generated and saved as 'gift_suggestion_workflow.html'")

if __name__ == "__main__":
    asyncio.run(generate_graph())