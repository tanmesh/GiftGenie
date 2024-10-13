# GiftGenie


https://github.com/user-attachments/assets/e997ea94-efce-4fe0-84b7-6f2525ad997c

# GiftGenie - AI-Powered Gift Suggestion App

GiftGenie is your AI-powered personal shopper that takes the stress out of gift-giving, providing thoughtful, personalized recommendations for any occasion.

## Tools Used
LlamaIndex workflows (Agent workflow), Toolhouse (Twitter Scraping), Apify (Amazon scraping)

## Inspiration
GiftGenie was inspired by the common challenge of finding the perfect gift for friends and loved ones. We wanted to create a tool that could analyze a person's interests and preferences, then suggest thoughtful and personalized gift ideas within a specified budget.

## What it does
GiftGenie is an AI-powered gift suggestion app that:

1. Analyzes tweets or any additional text to identify interests and preferences.
2. Maps these interests to relevant gift categories.
3. Generates specific gift ideas within a price range.
4. Debates the pros and cons of each gift idea.
5. Reasons over the debates to select the best gift suggestions.
6. Suggests Amazon search keywords for easy shopping.
7. Provides Amazon product links for the suggested gifts.

## How we built it
We built GiftGenie using:

- Python for the backend logic.
- LlamaIndex workflows for structuring our agent interactions.
- Streamlit for the user interface.
- OpenAI's GPT-4 model for natural language processing and reasoning.
- Apify for scraping Amazon product data.
- Asynchronous programming for improved performance.
- Toolhouse for X (Twitter) data retrieval.

## Challenges we ran into
1. Integrating multiple AI agents to work together seamlessly.
2. Ensuring the gift suggestions remained within the specified price range.
3. Optimizing the workflow to provide results in a reasonable timeframe.
4. Handling and displaying the complex, multi-step results in a user-friendly manner.
5. Parsing and extracting relevant information from X (Twitter) data.

## Accomplishments that we're proud of
1. Creating a fully functional AI-powered gift suggestion system.
2. Successfully implementing a multi-step workflow with different AI agents for each task.
3. Integrating real-time Amazon product data into our suggestions.
4. Developing a user-friendly interface that guides users through the gift suggestion process.
5. Implementing a robust logging system for debugging and tracking the app's performance.

## What we learned
1. How to structure and implement complex AI workflows using LlamaIndex.
2. Techniques for prompting and guiding AI models to produce specific types of output.
3. The importance of error handling and fallback options in AI-driven applications.
4. How to integrate third-party APIs (like Apify and Toolhouse) into our application for real-world data.
5. Effective ways to manage and process asynchronous operations in Python.

## What's next for GiftGenie - Gift Suggestion App
1. Implement user accounts to save gift suggestions and preferences.
2. Enhance the X (Twitter) data retrieval and analysis capabilities.
3. Add support for more e-commerce platforms beyond Amazon.
4. Implement a feedback system to improve gift suggestions over time.
5. Develop mobile apps for iOS and Android for easier access.
6. Expand language support for international users.
7. Optimize the performance of the gift suggestion workflow for faster results.
8. Enhance the debate and reasoning capabilities of the AI agents for more nuanced gift selections.
