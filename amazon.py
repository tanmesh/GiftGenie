import asyncio
from playwright.async_api import async_playwright
from dotenv import load_dotenv
import os
import sys
from datetime import datetime
import json

async def login_to_amazon(playwright):
    browser = await playwright.chromium.launch(headless=False)
    page = await browser.new_page()

    try:
        await page.goto('https://www.amazon.com/ap/signin?openid.pape.max_auth_age=0&openid.return_to=https%3A%2F%2Fwww.amazon.com%2F%3Fref_%3Dnav_ya_signin&openid.identity=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.assoc_handle=usflex&openid.mode=checkid_setup&openid.claimed_id=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0%2Fidentifier_select&openid.ns=http%3A%2F%2Fspecs.openid.net%2Fauth%2F2.0', wait_until='networkidle', timeout=60000)
        await asyncio.sleep(4)

        email_field = await page.wait_for_selector('#ap_email', state='visible', timeout=60000)
        await email_field.fill(email)
        print("Email field filled successfully")
        await asyncio.sleep(3)

        continue_button = await page.wait_for_selector('#continue', state='visible', timeout=30000)
        await continue_button.click()
        print("Clicked continue button")
        await asyncio.sleep(4)

        password_field = await page.wait_for_selector('#ap_password', state='visible', timeout=30000)
        await password_field.fill(password)
        print("Password field filled successfully")
        await asyncio.sleep(3)

        sign_in_button = await page.wait_for_selector('#signInSubmit', state='visible', timeout=30000)
        await sign_in_button.click()
        print("Clicked sign in button")
        await asyncio.sleep(4)

        await page.wait_for_load_state('networkidle', timeout=60000)

        if page.url.startswith('https://www.amazon.com/'):
            print('Login successful')
            return browser, page
        else:
            print('Login may have failed. Current URL:', page.url)
            return None, None

    except Exception as e:
        print(f'An error occurred during login: {e}')
        await page.screenshot(path='login_error.png')
        print(f"Login error screenshot saved as 'login_error.png'")
        return None, None

async def search_and_extract_results(page, search_term):
    try:
        await asyncio.sleep(5)

        search_bar = await page.wait_for_selector('#twotabsearchtextbox', state='visible', timeout=60000)
        await search_bar.click()
        await search_bar.fill(search_term)
        await page.keyboard.press('Enter')

        await page.wait_for_selector('div[data-component-type="s-search-result"]', timeout=60000)

        for _ in range(3):
            await page.evaluate('window.scrollBy(0, window.innerHeight)')
            await asyncio.sleep(2)

        results = await page.evaluate('''() => {
            const items = Array.from(document.querySelectorAll('div[data-component-type="s-search-result"]'));
            return items.slice(0, 10).map(item => {
                const titleElement = item.querySelector('h2 a span');
                const linkElement = item.querySelector('h2 a');
                const priceElement = item.querySelector('.a-price-whole');
                const ratingElement = item.querySelector('.a-icon-star-small .a-icon-alt');
                const sponsoredElement = item.querySelector('.s-sponsored-label-info-icon');
                const purchaseInfoElement = item.querySelector('.a-size-base.a-color-secondary');
                
                let purchaseInfo = '';
                if (purchaseInfoElement) {
                    const text = purchaseInfoElement.innerText;
                    const match = text.match(/(\d+,?\d*) bought in past month/);
                    if (match) {
                        purchaseInfo = match[0];
                    }
                }
                
                return {
                    title: titleElement ? titleElement.innerText : 'N/A',
                    product_url: linkElement ? 'https://www.amazon.com' + linkElement.getAttribute('href') : 'N/A',
                    price: priceElement ? priceElement.innerText : 'N/A',
                    rating: ratingElement ? ratingElement.innerText : 'N/A',
                    sponsored: sponsoredElement ? 'Yes' : 'No',
                    purchase_info: purchaseInfo || 'N/A'
                };
            });
        }''')

        current_url = page.url
        page_title = await page.title()

        return results, current_url, page_title

    except Exception as e:
        print(f"An error occurred during search and extraction: {e}")
        await page.screenshot(path='search_error.png')
        print(f"Search error screenshot saved as 'search_error.png'")
        return None, page.url, await page.title()

def create_json_file(search_term, results, current_url, page_title):
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    time_minutes = now.hour * 60 + now.minute

    data = {
        "search_term": search_term,
        "date": date_str,
        "time_minutes": time_minutes,
        "current_url": current_url,
        "page_title": page_title,
        "results": results
    }

    filename = f"search_results_{date_str}_{time_minutes}.json"
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"JSON file '{filename}' has been created in the local directory.")

async def login_search_amazon():
    load_dotenv()

    global email, password
    email = os.getenv("EMAIL")
    password = os.getenv("PASSWORD")

    if not email or not password:
        print("Error: EMAIL or PASSWORD environment variables are not set.")
        return

    search_term = "wireless mouse"
    
    async with async_playwright() as playwright:
        browser, page = await login_to_amazon(playwright)
        if browser and page:
            try:
                results, current_url, page_title = await search_and_extract_results(page, search_term)
                
                print(f"\nCurrent URL: {current_url}")
                print(f"Page Title: {page_title}\n")
                
                if results:
                    print(f"--- Search Results for '{search_term}' ---\n")
                    for i, result in enumerate(results, 1):
                        print(f"Result {i}:")
                        print(f"Title: {result.get('title', 'N/A')}")
                        print(f"Product URL: {result.get('product_url', 'N/A')}")
                        print(f"Price: {result.get('price', 'N/A')}")
                        print(f"Rating: {result.get('rating', 'N/A')}")
                        print(f"Sponsored: {result.get('sponsored', 'N/A')}")
                        print(f"Purchase Info: {result.get('purchase_info', 'N/A')}")
                        print("---")
                    
                    create_json_file(search_term, results, current_url, page_title)
                else:
                    print("No results found or an error occurred during extraction.")
                
            except Exception as e:
                print(f"An error occurred: {e}")
                await page.screenshot(path='error.png')
                print(f"Error screenshot saved as 'error.png'")
            
            print("Press Enter to close the browser...")
            input()
            await browser.close()
        else:
            print("Login failed. Unable to perform search and extract results.")

def run_async_login_search():
    loop = asyncio.get_event_loop()
    if loop.is_running():
        loop.create_task(login_search_amazon())
    else:
        loop.run_until_complete(login_search_amazon())

# This function can be called from both synchronous and asynchronous contexts
def main():
    run_async_login_search()

if __name__ == "__main__":
    main()