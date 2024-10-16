import asyncio
import streamlit as st
from gift_suggestion_workflow import (
    GiftSuggestionWorkflow,
    Context,
    StartEvent,
    AmazonKeywordGeneratorEvent,
    AmazonProductLinkEvent,  # Add this import
)
import traceback
from searchx import search_tweets
import os
from datetime import datetime
import random
from collections import defaultdict
import sys

st.set_page_config(page_title="Gift Genie", page_icon="🎁", layout="wide")

st.markdown(
    """
    <style>
    .reportview-container .main .block-container {
        padding-left: 5rem;
        padding-right: 5rem;
    }
    .stProgress > div > div > div > div {
        background-color: #f63366;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🎁 Gift Genie 🎁")

# Initialize log_output in session state if it doesn't exist
if 'log_output' not in st.session_state:
    st.session_state.log_output = []

def log_print(*args, **kwargs):
    message = " ".join(map(str, args))
    print(message, flush=True)  # Print to console immediately
    st.session_state.log_output.append(message)
    
    # Write to log file
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    log_filename = datetime.now().strftime("%Y-%m-%d-%H-%M") + ".txt"
    log_path = os.path.join(log_dir, log_filename)
    with open(log_path, "a") as log_file:
        log_file.write(message + "\n")
        log_file.flush()  # Ensure it's written to the file immediately

async def run_workflow(price_ceiling, twitter_handle, additional_text, progress_bar):
    workflow = GiftSuggestionWorkflow(
        price_ceiling=price_ceiling,
        log_print_func=log_print,
        timeout=600,
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

    progress_bar.progress(0)
    
    with st.expander("Step 1: Analyzing Tweets and Text 🧐", expanded=True):
        init_event = await workflow.initialize(ctx, StartEvent())
        st.subheader("Tweets Extracted and Additional Information")
        for tweet in init_event.tweets:
            st.markdown(f"- {tweet}")
        interest_event = await workflow.tweet_analyzer(ctx, init_event)
        st.subheader("Interests Identified")
        st.write(interest_event.interests)
    progress_bar.progress(20)

    with st.expander("Step 2: Mapping Interests to Gift Categories", expanded=True):
        st.subheader("Interest Mapping")
        gift_categories_event = await workflow.interest_mapper(ctx, interest_event)
        st.subheader("Gift Categories")
        st.text(gift_categories_event.gift_categories)
        # categories = gift_categories_event.gift_categories.split(", ")
        # for i, category in enumerate(categories, 1):
        #     st.markdown(f"{i}. {category}")
    progress_bar.progress(40)

    with st.expander("Step 3: 💡 Generating Gift Ideas", expanded=True):
        gift_ideas_event = await workflow.gift_idea_generator(ctx, gift_categories_event)
        st.subheader("Gift Ideas by Category")
        
        # Group ideas by category
        categorized_ideas = defaultdict(list)
        for idea in gift_ideas_event.gift_ideas:
            category, item = idea.split(": ", 1)
            categorized_ideas[category].append(item)
        
        # Display ideas by category
        for category, ideas in categorized_ideas.items():
            st.write(f"**{category}**")
            for idea in ideas:
                st.markdown(f"- {idea}")
        
        # Score and select top 5 gift ideas based on relevance to user's interests
        def score_idea(idea, interests):
            return sum(interest.lower() in idea.lower() for interest in interests.split(','))

        interests = interest_event.interests
        scored_ideas = [(idea, score_idea(idea, interests)) for idea in gift_ideas_event.gift_ideas]
        top_ideas = sorted(scored_ideas, key=lambda x: x[1], reverse=True)[:5]
        
        st.subheader("Top 5 Gift Ideas Based on User Interests")
        for idea, score in top_ideas:
            st.markdown(f"- {idea} (Relevance Score: {score})")

    progress_bar.progress(60)

    with st.expander("Step 4: 🥊 Debating Gift Ideas 🥊", expanded=True):
        gift_debates_event = await workflow.mediation_agent(ctx, gift_ideas_event)
        st.subheader("Gift Debates")
        for gift, debate in gift_debates_event.debates.items():
            st.write(f"**{gift}**")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("🟢 **Pro:**")
                st.markdown(debate['pro'])
            with col2:
                st.markdown("🔴 **Con:**")
                st.markdown(debate['con'])
            st.markdown("---")
    progress_bar.progress(80)

    with st.expander("Step 5: Reasoning Over Gift Debates 🤔", expanded=True):
        gift_reasoner_event = await workflow.gift_reasoner(ctx, gift_debates_event)
        st.subheader("Final Gift Selections")
        for gift, reasons in gift_reasoner_event.gift_ideas.items():
            st.markdown(f"**{gift}**")
            for reason in reasons:
                st.markdown(f"*Rationale:* {reason}")
            st.markdown("---")
    progress_bar.progress(90)

    with st.expander("Step 6: Generating Amazon Search Keywords ✍️", expanded=True):
        amazon_keyword_event = await workflow.amazon_keyword_generator(ctx, gift_reasoner_event)
        st.subheader("Amazon Search Keywords")
        for keyword in amazon_keyword_event.amazon_keywords:
            st.markdown(f"- {keyword}")
    progress_bar.progress(95)

    with st.expander("Step 7: Generating Amazon Product Links 📀", expanded=True):
        st.subheader("Amazon Product Links")
        product_links = []
        for keyword in amazon_keyword_event.amazon_keywords:
            print(f"Generating product links for keyword: {keyword}")
            product_link_event = await workflow.amazon_product_link_generator(
                ctx, AmazonProductLinkEvent(keyword=keyword)
            )
            print(f"Product link event: {product_link_event}")
            product_links.append(product_link_event)

        print("\n--- Amazon Product Links ---")
        print(product_links)
        print("----------------------------\n")

        st.subheader("Amazon Product Links")
        for product_link in product_links:
            with st.container():
                col1, col2 = st.columns([1, 3])
                with col1:
                    if product_link.product_image:
                        st.image(product_link.product_image, width=100)
                    else:
                        st.write("No image available")
                with col2:
                    st.write(f"**{product_link.product_title[:50]}...**" if product_link.product_title else "Title not available")
                    price_text = f"${product_link.product_price:.2f}" if product_link.product_price and product_link.product_price != 'N/A' else "Price not available"
                    rating_stars = '⭐' * int(float(product_link.product_rating)) if product_link.product_rating and product_link.product_rating != 'N/A' else ""
                    st.write(f"{price_text} | {rating_stars}")
                    if product_link.product_links:
                        st.markdown(f"[View]({product_link.product_links})")
                    else:
                        st.write("Link not available")
    progress_bar.progress(100)

    return amazon_keyword_event

def main():
    price_ceiling = st.sidebar.number_input(
        "Set Price Ceiling ($) 💰", min_value=1, max_value=1000, value=30
    )
    twitter_handle = st.sidebar.text_input(
        "Twitter Handle (optional) 🦜", help="Enter with or without '@'"
    )
    additional_text = st.sidebar.text_area(
        "Additional Information (optional) 📝",
        help="Enter any additional text to analyze",
    )

    if st.button("✨ Let the GiftGenie Grant Your Wish ✨"):
        progress_bar = st.progress(0)
        progress_text = st.empty()
        try:
            progress_text.text("Starting the gift suggestion process...")
            asyncio.run(
                run_workflow(price_ceiling, twitter_handle, additional_text, progress_bar)
            )
            progress_text.text("Gift suggestions generated successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            traceback.print_exc(file=sys.stdout)
            log_print(f"Error: {str(e)}")  # Log the error
        finally:
            progress_bar.empty()
            progress_text.empty()

    st.sidebar.info("Note: This process may take a few minutes to complete.")

    # Display logs
    if st.session_state.log_output:
        with st.expander("✨ 📝 Our Notes 📝  ✨", expanded=False):
            for log in st.session_state.log_output:
                st.text(log)

if __name__ == "__main__":
    main()