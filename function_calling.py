import os
from typing import List, Dict
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, Document, Settings
from llama_index.llms.openai import OpenAI
from llama_index.core.storage import StorageContext

# Initial dummy data
twitter_feed = [
    "Just finished a great workout at the gym! #fitness #health",
    "Can't wait for my camping trip next weekend. Need to get some gear! #outdoors #adventure",
    "Loving my new smartphone. The camera is amazing! #tech #photography",
    "Trying to eat healthier. Any good cookbook recommendations? #cooking #health",
    "Working on a new coding project. Python is so fun! #programming #tech"
]

amazon_products = [
    {"name": "Fitness Tracker", "category": "Health & Fitness", "price": 49.99},
    {"name": "Camping Tent", "category": "Outdoors", "price": 129.99},
    {"name": "Smartphone Camera Lens Kit", "category": "Electronics", "price": 39.99},
    {"name": "Healthy Cooking Cookbook", "category": "Books", "price": 24.99},
    {"name": "Python Programming Book", "category": "Books", "price": 34.99},
    {"name": "Yoga Mat", "category": "Health & Fitness", "price": 29.99},
    {"name": "Hiking Backpack", "category": "Outdoors", "price": 79.99},
    {"name": "Wireless Earbuds", "category": "Electronics", "price": 89.99},
    {"name": "Air Fryer Cookbook", "category": "Books", "price": 19.99},
    {"name": "Raspberry Pi Starter Kit", "category": "Electronics", "price": 59.99}
]

def get_openai_key():
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    os.environ["OPENAI_API_KEY"] = openai_api_key

def create_index(data: List[str], index_name: str) -> VectorStoreIndex:
    documents = [Document(text=item) for item in data]
    Settings.llm = OpenAI()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=f'./{index_name}')
    return index

def analyze_twitter_feed(feed: List[str]) -> str:
    index = create_index(feed, "twitter_index")
    query_engine = index.as_query_engine()
    query = "Analyze the user's interests based on their tweets and provide a summary of their main interests."
    response = query_engine.query(query)
    return response.response

def recommend_products(interests: str, products: List[Dict]) -> str:
    product_data = [f"{p['name']} - {p['category']} - ${p['price']}" for p in products]
    index = create_index(product_data, "product_index")
    query_engine = index.as_query_engine()
    query = f"Based on the user's interests: {interests}, recommend 3 products from the available list that would be most relevant."
    response = query_engine.query(query)
    return response.response

def update_twitter_feed(user_input: str, current_feed: List[str]) -> List[str]:
    # Generate a new tweet based on user input
    new_tweet = f"Excited about {user_input}! #{user_input.replace(' ', '')}"
    
    # Add the new tweet to the beginning of the feed
    updated_feed = [new_tweet] + current_feed
    
    # Keep only the 5 most recent tweets
    return updated_feed[:5]

def main():
    get_openai_key()
    global twitter_feed

    while True:
        user_input = input("What would you like to do? (Type 'exit' to quit): ")
        
        if user_input.lower() == 'exit':
            break

        try:
            # Update Twitter feed based on user input
            twitter_feed = update_twitter_feed(user_input, twitter_feed)

            print("Analyzing updated Twitter feed...")
            user_interests = analyze_twitter_feed(twitter_feed)
            print(f"User Interests: {user_interests}")

            print("\nRecommending products...")
            recommendations = recommend_products(user_interests, amazon_products)
            print(f"Product Recommendations: {recommendations}")

        except Exception as e:
            print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()