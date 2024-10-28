from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import asyncio
import json
import os
import sys
import traceback
from datetime import datetime

from gift_suggestion_workflow import (
    GiftSuggestionWorkflow,
    Context,
    StartEvent,
    AmazonKeywordGeneratorEvent,
    AmazonProductLinksEvent,
)
from searchx import search_tweets

app = Flask(__name__)
CORS(app, resources={r"/generate_gift_suggestions": {"origins": "*"}})

# Initialize the status dictionary
status = {
    "tweets": [],
    "interests": [],
    "gift_categories": [],
    "gift_ideas": [],
    "debating_ideas": [],
    "gift_reasoning": [],
    "amazon_keywords": [],
    "amazon_recommendation": [],
}


async def run_workflow(
    price_ceiling: float, twitter_handle: str, additional_text: str, log_print
):
    workflow = GiftSuggestionWorkflow(
        price_ceiling=price_ceiling,
        log_print_func=log_print,
        timeout=1200,
        verbose=True,
    )
    ctx = Context(workflow)

    if twitter_handle:
        twitter_handle = twitter_handle.lstrip("@")
        tweet_data = search_tweets(twitter_handle)
        ctx.data["tweets"] = [tweet["text"] for tweet in tweet_data]
    else:
        ctx.data["tweets"] = []

    ctx.data["twitter_handle"] = twitter_handle
    ctx.data["additional_text"] = additional_text

    init_event = await workflow.initialize(ctx, StartEvent())
    status["tweets"] = init_event.tweets

    interest_event = await workflow.tweet_analyzer(ctx, init_event)
    status["interests"] = interest_event.interests

    gift_categories_event = await workflow.interest_mapper(ctx, interest_event)
    status["gift_categories"] = gift_categories_event.gift_categories

    gift_ideas_event = await workflow.gift_idea_generator(ctx, gift_categories_event)
    status["gift_ideas"] = gift_ideas_event.gift_ideas

    debates_event = await workflow.gift_debater(ctx, gift_ideas_event)
    status["debating_ideas"] = debates_event.debates

    final_gifts_event = await workflow.gift_reasoner(ctx, debates_event)
    status["gift_reasoning"] = final_gifts_event.gift_ideas

    keywords_event = await workflow.amazon_keyword_generator(
        ctx, AmazonKeywordGeneratorEvent(gift_ideas=final_gifts_event.gift_ideas)
    )
    amazon_keywords = keywords_event.amazon_keywords or ["Gift under $40"]
    status["amazon_keywords"] = amazon_keywords

    product_links = []
    for keyword in amazon_keywords:
        product_links_event = await workflow.amazon_product_link_generator(ctx, keyword)
        product_links.append(
            {
                "links": product_links_event.product_links,
                "image": product_links_event.product_image,
                "title": product_links_event.product_title,
                "price": product_links_event.product_price,
                "rating": product_links_event.product_rating,
            }
        )
    status["amazon_recommendation"] = product_links

    # amazon_keywords = ["Gift under $40"]

    # product_links = []
    # for keyword in amazon_keywords:
    #     product_links_event = await workflow.amazon_product_link_generator(ctx, keyword)
    #     print(f'Product Link Event: {product_links_event}')
    #     product_links.append({
    #         "links": product_links_event.product_links,
    #         "image": product_links_event.product_image,
    #         "title": product_links_event.product_title,
    #         "price": product_links_event.product_price,
    #         "rating": product_links_event.product_rating
    #     })
    # status["amazon_recommendation"] = product_links
    # print(f'Product Links: {product_links}')


# Set up logging
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_filename = f"{datetime.now().strftime('%Y-%m-%d-%H-%M')}.txt"
log_path = os.path.join(log_dir, log_filename)


def log_print(*args, **kwargs):
    message = " ".join(map(str, args))
    print(message, flush=True)
    with open(log_path, "a") as log_file:
        log_file.write(f"{message}\n")
        log_file.flush()


@app.route("/generate_gift_suggestions", methods=["GET"])
def get_status():
    return jsonify(status) or {}


@app.route("/generate_gift_suggestions", methods=["POST"])
async def generate_gift_suggestions():
    payload = request.get_json()

    price_ceiling = float(payload.get("price_ceiling", 30))
    twitter_handle = payload.get("twitter_handle", "")
    additional_text = payload.get("additional_text", "")

    sys.excepthook = lambda type, value, tb: log_print(
        "".join(traceback.format_exception(type, value, tb))
    )

    asyncio.create_task(
        run_workflow(price_ceiling, twitter_handle, additional_text, log_print)
    )

    return jsonify({"status": "Workflow initiated"}), 202


if __name__ == "__main__":
    app.run(debug=True)
