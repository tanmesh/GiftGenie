from flask import Flask, request, jsonify, Response
from flask_cors import CORS
import time
import json
import os
import sys
import traceback
from datetime import datetime
from main import run_workflow
from searchx import search_tweets
from gift_suggestion_workflow import (
    GiftSuggestionWorkflow,
    Context,
    StartEvent,
    AmazonKeywordGeneratorEvent,
)


app = Flask(__name__)
CORS(app)

# Initialize the status dictionary (same as before)
status = {
    "tweets": [
        "Just finished a great workout at the gym!",
        "Can't wait for my camping trip next weekend. Need to get some gear!",
        "Loving my new smartphone. The camera is amazing!",
    ],
    "interests": ["Fitness", "Outdoor Activities", "Technology"],
    "categories": ["Fitness Gear", "Camping Equipment", "Tech Gadgets"],
    "gift_ideas": ["Yoga Mat", "Hiking Backpack", "Smartwatch"],
    "debating_ideas": [
        "Is a smartwatch a good gift for a tech enthusiast?",
        "Should I get a yoga mat or a gym membership?",
    ],
    "reasoning": [
        "Smartwatches are practical for fitness tracking and daily use.",
        "Yoga mats are great for home workouts and yoga enthusiasts.",
    ],
    "amazon_keywords": [
        "fitness gear under $40",
        "camping essentials",
        "smartwatch deals",
    ],
    "amazon_recommendation": {
        "Amazon Basics USB-C to USB-C 2.0 Fast Charger Cable, Black 6-Foot 1-Pack": {
            "info": "USB-IF Certified, 480Mbps speed, for Apple iPhone 15, iPad, Samsung Galaxy, tablets, laptops",
            "image": "https://m.media-amazon.com/images/I/61JBLA+DKLL._AC_SL1070_.jpg",
            "price": "$11.69",
            "rating": "4.6",
        },
    },
}


# # Initialize the status dictionary (same as before)
# status = {
#     "tweets": [],
#     "interests": [],
#     "categories": [],
#     "gift_ideas": [],
#     "debating_ideas": [],
#     "reasoning": [],
#     "amazon_keywords": [],
#     "amazon_recommendation": [],
# }


# async def run_workflow(price_ceiling, twitter_handle, additional_text, log_print):
#     workflow = GiftSuggestionWorkflow(
#         price_ceiling=price_ceiling,
#         log_print_func=log_print,
#         timeout=1200,
#         verbose=True,
#     )
#     ctx = Context(workflow)

#     if twitter_handle:
#         # Remove '@' if present
#         twitter_handle = twitter_handle.lstrip("@")
#         tweet_data = search_tweets(twitter_handle)
#         ctx.data["tweets"] = [tweet["text"] for tweet in tweet_data]
#     else:
#         ctx.data["tweets"] = []

#     ctx.data["twitter_handle"] = twitter_handle
#     ctx.data["additional_text"] = additional_text


#     init_event = await workflow.initialize(ctx, StartEvent())
#     print(f"init_event.tweets: {init_event.tweets}")
#     status["tweets"] = init_event.tweets

#     interest_event = await workflow.tweet_analyzer(ctx, init_event)
#     print(f'interest_event.interests: {interest_event.interests}')
#     status["interests"] = interest_event.interests

#     gift_categories_event = await workflow.interest_mapper(ctx, interest_event)
#     status["gift_categories"] = gift_categories_event.gift_categories    

#     gift_ideas_event = await workflow.gift_idea_generator(ctx, gift_categories_event)
#     status["gift_ideas"] = gift_ideas_event.gift_ideas    

#     debates_event = await workflow.gift_debater(ctx, gift_ideas_event)
#     status["debates"] = debates_event.debates

#     final_gifts_event = await workflow.gift_reasoner(ctx, debates_event)
#     gifts = []
#     for gift in final_gifts_event.gift_ideas:
#         gifts.append(gift)
#     status["gift_categories"] = gifts


#     keywords_event = await workflow.amazon_keyword_generator(
#         ctx, AmazonKeywordGeneratorEvent(gift_ideas=final_gifts_event.gift_ideas)
#     )    
#     amazon_keywords = keywords_event.amazon_keywords
#     # Ensure we have at least one keyword
#     if not amazon_keywords:        
#         amazon_list = ["Gift under $40"]  # Fallback keyword

#     if isinstance(amazon_list, str):
#         keywords = amazon_list.split(",")
#     else:
#         keywords = amazon_list
#     status["amazon_keywords"] = amazon_keywords


    
#     product_links = []
#     for keyword in keywords:
#         print(f"Generating product links for keyword: {keyword}")
#         product_links_event = await workflow.amazon_product_link_generator(
#             ctx, keyword
#         )
#         print(f"Product links event: {product_links_event}")
#         product_links.append(product_links_event)
#     status["amazon_recommendation"] = product_links
    

@app.route("/generate_gift_suggestions", methods=["POST"])
def generate_gift_suggestions():
    payload = request.get_json()

    price_ceiling = payload.get("price_ceiling", 30)
    twitter_handle = payload.get("twitter_handle", "")
    additional_text = payload.get("additional_text", "")

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M") + ".txt"
    log_path = os.path.join(log_dir, log_filename)

    def log_print(*args, **kwargs):
        message = " ".join(map(str, args))
        print(message, flush=True)
        with open(log_path, "a") as log_file:
            log_file.write(message + "\n")
            log_file.flush()

    sys.excepthook = lambda type, value, tb: log_print(
        "".join(traceback.format_exception(type, value, tb))
    )

    def generate():
        # run_workflow(price_ceiling, twitter_handle, additional_text, log_print)
        try:
            for key, value in status.items():
                time.sleep(4)  # 4-second delay
                print(f"Sending data for key: {key}")  # Debug print
                yield json.dumps({key: value}) + "\n"
        except Exception as e:
            print(f"Error occurred: {str(e)}")  # Debug print
            yield json.dumps({"error": str(e)}) + "\n"

    return Response(generate(), mimetype="application/json")


if __name__ == "__main__":
    app.run(debug=True)
