from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Document
from llama_index.llms.openai import OpenAI
from llama_index.core import Settings
from llama_index.core.storage import StorageContext
import os
from dotenv import load_dotenv

# Dummy data
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
    # Load environment variables from .env file
    load_dotenv()

    # Get OpenAI API key from environment variable
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")

    os.environ["OPENAI_API_KEY"] = openai_api_key

def create_index(data, index_name):
    documents = [Document(text=item) for item in data]
    Settings.llm = OpenAI()
    index = VectorStoreIndex.from_documents(documents)
    index.storage_context.persist(persist_dir=f'./{index_name}')
    return index

def load_index(index_name):
    Settings.llm = OpenAI()
    storage_context = StorageContext.from_defaults(persist_dir=f'./{index_name}')
    return VectorStoreIndex.from_storage_context(storage_context)

# Create an agent to analyze the Twitter feed
def analyze_twitter_feed(feed):
    index = create_index(feed, "twitter_index")
    query_engine = index.as_query_engine()
    query = "Analyze the user's interests based on their tweets and provide a summary of their main interests."
    response = query_engine.query(query)
    return response.response

# Create an agent to recommend Amazon products
def recommend_products(interests, products):
    product_data = [f"{p['name']} - {p['category']} - ${p['price']}" for p in products]
    index = create_index(product_data, "product_index")
    query_engine = index.as_query_engine()
    query = f"Based on the user's interests: {interests}, recommend 3 products from the available list that would be most relevant."
    response = query_engine.query(query)
    return response.response

# Main workflow
def main():
    get_openai_key()
    print("Analyzing Twitter feed...")
    user_interests = analyze_twitter_feed(twitter_feed)
    print(f"User Interests: {user_interests}")
    
    print("\nRecommending products...")
    recommendations = recommend_products(user_interests, amazon_products)
    print(f"Product Recommendations: {recommendations}")

if __name__ == "__main__":
    main()
