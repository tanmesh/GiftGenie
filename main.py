import os
import sys
import traceback
import asyncio
from datetime import datetime
import streamlit as st
from searchx import search_tweets
from gift_suggestion_workflow import GiftSuggestionWorkflow, Context, StartEvent

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
    workflow = GiftSuggestionWorkflow(price_ceiling=price_ceiling, log_print_func=log_print, timeout=1200, verbose=True)
    ctx = Context(workflow)
    
    if twitter_handle:
        # Remove '@' if present
        twitter_handle = twitter_handle.lstrip('@')
        tweet_data = search_tweets(twitter_handle)
        ctx.data["tweets"] = [tweet['text'] for tweet in tweet_data]
    else:
        ctx.data["tweets"] = []
    
    ctx.data["twitter_handle"] = twitter_handle
    ctx.data["additional_text"] = additional_text

    with st.spinner("Analyzing tweets and text..."):
        init_event = await workflow.initialize(ctx, StartEvent())
        st.subheader("Tweets Extracted and Additional Information Considered")
        st.write(interest_event.tweets)
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

    with st.spinner("Generating Amazon search keywords..."):
            keywords_event = await workflow.amazon_keyword_generator(ctx, final_gifts_event)
            st.subheader("Amazon Search Keywords")
            st.write(keywords_event)
            return keywords_event

def main():
    price_ceiling = st.sidebar.number_input("Set Price Ceiling ($)", min_value=1, max_value=1000, value=30)
    twitter_handle = st.sidebar.text_input("Twitter Handle (optional) 🐦", help="Enter with or without '@'")
    additional_text = st.sidebar.text_area("Additional Information (optional) 📝", help="Enter any additional text to analyze")

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

    sys.excepthook = lambda type, value, tb: log_print("".join(traceback.format_exception(type, value, tb)))

    st.write("This app uses a GiftSuggestionWorkflow to analyze tweets and suggest gift ideas.")
    st.write("Click the button below to start the gift suggestion process.")

    if st.button("✨ Let the GiftGenie Grant Your Wish ✨"):
        try:
            log_print(f"Starting workflow with price ceiling: ${price_ceiling}")
            amazon_keywords = asyncio.run(run_workflow(price_ceiling, twitter_handle, additional_text, log_print))
            st.success("Gift suggestions generated successfully!")
            st.subheader("Amazon Search Keywords")
            st.write(amazon_keywords)
        except Exception as e:
            log_print(f"An error occurred: {str(e)}")
            traceback.print_exc(file=sys.stdout)
            st.error(f"An error occurred: {str(e)}")

    st.info("Note: This process may take a few minutes to complete.")

if __name__ == "__main__":
    main()