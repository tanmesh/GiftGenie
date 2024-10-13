import ast
import os
import sys
import traceback
import asyncio
from datetime import datetime
import streamlit as st
from searchx import search_tweets
from gift_suggestion_workflow import (
    GiftSuggestionWorkflow,
    Context,
    StartEvent,
    AmazonKeywordGeneratorEvent,
)

st.set_page_config(page_title="GiftGenie", page_icon="🎁", layout="wide")

st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        padding-left: 5rem;
        padding-right: 5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎁 GiftGenie 🎁")


async def run_workflow(price_ceiling, twitter_handle, additional_text, log_print):
    workflow = GiftSuggestionWorkflow(
        price_ceiling=price_ceiling,
        log_print_func=log_print,
        timeout=1200,
        verbose=True,
    )
    ctx = Context(workflow)

    if twitter_handle:
        # Remove '@' if present
        twitter_handle = twitter_handle.lstrip("@")
        tweet_data = search_tweets(twitter_handle)
        ctx.data["tweets"] = [tweet["text"] for tweet in tweet_data]
    else:
        ctx.data["tweets"] = []

    ctx.data["twitter_handle"] = twitter_handle
    ctx.data["additional_text"] = additional_text

    with st.spinner("Analyzing tweets and text..."):
        init_event = await workflow.initialize(ctx, StartEvent())
        st.subheader("Tweets Extracted and Additional Information Considered")
        st.write(init_event.tweets)
        interest_event = await workflow.tweet_analyzer(ctx, init_event)
        st.subheader("Interests Identified")
        st.write(interest_event.interests)

    with st.spinner("Mapping interests to gift categories..."):
        gift_categories_event = await workflow.interest_mapper(ctx, interest_event)
        st.subheader("Gift Categories")
        st.write(gift_categories_event.gift_categories)

    with st.spinner("Generating gift ideas..."):
        gift_ideas_event = await workflow.gift_idea_generator(ctx, gift_categories_event)
        st.subheader("Gift Ideas")
        st.write(gift_ideas_event.gift_ideas)

    with st.spinner("Debating gift ideas..."):
        debates_event = await workflow.gift_debater(ctx, gift_ideas_event)
        st.subheader("Gift Debates")
        st.text(debates_event.debates)

    with st.spinner("Reasoning over gift debates..."):
        final_gifts_event = await workflow.gift_reasoner(ctx, debates_event)
        st.subheader("Final Gift Selections")
        for gift in final_gifts_event.gift_ideas:
            st.write(gift)

    # final_gifts_event = AmazonKeywordGeneratorEvent(gift_ideas=[])
    # final_gifts_event.gift_ideas = [
    #     "1. Personalized Photo Frame\nRationale: A thoughtful and sentimental gift that can showcase cherished memories.",
    #     "2. Portable Bluetooth Speaker\nRationale: Perfect for music lovers and outdoor enthusiasts.",
    #     "3. Gourmet Chocolate Gift Set\nRationale: A delicious treat that appeals to most people's taste buds.",
    # ]
    with st.spinner("Generating Amazon search keywords..."):
        keywords_event = await workflow.amazon_keyword_generator(
            ctx, AmazonKeywordGeneratorEvent(gift_ideas=final_gifts_event.gift_ideas)
        )
        
        keywords_list = keywords_event.amazon_keywords
        # # Extract the content from the AgentChatResponse
        # keywords_list = ast.literal_eval(keywords_event.strip())
        # if not isinstance(keywords_list, list):
        #     print(f"keywords_list is not a list: {keywords_list}")
        #     keywords_list = [keywords_event.response]
        # keywords_list = [
        #     keyword for keyword in keywords_list if keyword
        # ]

        print("\n--- Amazon Search Keywords ---")
        print(keywords_list)
        print("----------------------------\n")

        # Ensure we have at least one keyword
        if not keywords_list:
            st.error("Failed to generate valid keywords. Please try again.")
            keywords_list = ["Gift under $40"]  # Fallback keyword

        # Display the generated Amazon keywords
        st.subheader("Amazon Search Keywords")
        if isinstance(keywords_list, str):
            keywords = keywords_list.split(",")
        else:
            keywords = keywords_list
        for keyword in keywords:
            st.write(f"- {keyword.strip()}")

    with st.spinner("Generating Amazon product links..."):
        product_links = []
        for keyword in keywords:
            print(f"Generating product links for keyword: {keyword}")
            product_links_event = await workflow.amazon_product_link_generator(
                ctx, keyword
            )
            print(f"Product links event: {product_links_event}")
            product_links.append(product_links_event)

        print("\n--- Amazon Product Links ---")
        print(product_links)
        print("----------------------------\n")

        st.subheader("Amazon Product Links")
        for product_link in product_links:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    st.image(product_link.product_image, width=100)
                with col2:
                    st.write(f"**{product_link.product_title[:50]}...**")
                    st.write(
                        f"${product_link.product_price:.2f} | {'⭐' * int(product_link.product_rating)}"
                    )
                    st.markdown(f"[View]({product_link.product_links})")
            st.markdown("---")


def main():
    price_ceiling = st.sidebar.number_input(
        "Set Price Ceiling ($)", min_value=1, max_value=1000, value=30
    )
    twitter_handle = st.sidebar.text_input(
        "Twitter Handle (optional) 🐦", help="Enter with or without '@'"
    )
    additional_text = st.sidebar.text_area(
        "Additional Information (optional) 📝",
        help="Enter any additional text to analyze",
    )

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

    st.write(
        "This app uses a GiftSuggestionWorkflow to analyze tweets and suggest gift ideas."
    )
    st.write("Click the button below to start the gift suggestion process.")

    if st.button("✨ Let the GiftGenie Grant Your Wish ✨"):
        try:
            log_print(f"Starting workflow with price ceiling: ${price_ceiling}")
            keywords_event = asyncio.run(
                run_workflow(price_ceiling, twitter_handle, additional_text, log_print)
            )
            st.success("Gift suggestions generated successfully!")
            # st.subheader("Amazon Search Keywords")
            # if (
            #     hasattr(keywords_event, "amazon_keywords")
            #     and keywords_event.amazon_keywords
            # ):
            #     for keyword in keywords_event.amazon_keywords:
            #         st.write(keyword)
            # else:
            #     st.write("No Amazon keywords were generated.")
        except Exception as e:
            log_print(f"An error occurred: {str(e)}")
            traceback.print_exc(file=sys.stdout)
            st.error(f"An error occurred: {str(e)}")

    st.info("Note: This process may take a few minutes to complete.")


if __name__ == "__main__":
    main()
