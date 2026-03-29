import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def scrape_sunmarke():
    print("Starting raw extraction from https://www.sunmarke.com/...")
    
    browser_config = BrowserConfig(headless=True)
    run_config = CrawlerRunConfig(cache_mode=CacheMode.BYPASS)

    async with AsyncWebCrawler(config=browser_config) as crawler:
        # Step 1: Discover pages from the homepage
        result = await crawler.arun(url="https://www.sunmarke.com/", config=run_config)
        
        if not result.success:
            print(f"Error: {result.error_message}")
            return []

        # We extract the 'href' from each link dictionary
        all_links = [link['href'] for link in result.links.get('internal', [])]
        
        # Broad filter: Keep all school-related info, exclude legal/system pages

        keywords = ['admission', 'fee', 'curriculum', 'facility', 'about', 
                    'learning', 'primary', 'secondary', 'sixth-form', 'contact',
                     'timing', 'calendar', 'result', 'academic', 'parent', 'faq'
]
        target_links = list(set([
            link for link in all_links 
            if 'sunmarke.com' in link 
            and any(k in link.lower() for k in keywords)
            and not any(x in link.lower() for x in ['privacy', 'terms', 'cookie', 'login', 'search'])
        ]))

        print(f"Found {len(target_links)} target pages. Fetching content.")

        # Step 2: Scrape content in parallel (limiting to 25)
        results = await crawler.arun_many(urls=target_links[:25], config=run_config)
        
        raw_storage = []
        for res in results:
            if res.success:
                raw_storage.append({
                    "url": res.url,
                    "markdown": res.markdown
                })
        
        return raw_storage

async def main():
    raw_data = await scrape_sunmarke()
    
    # Save for the next stage (database.py)
    with open("raw_data.json", "w", encoding="utf-8") as f:
        json.dump(raw_data, f, indent=4)
    
    print(f"Extraction complete. Saved {len(raw_data)} pages to raw_data.json.")

if __name__ == "__main__":
    asyncio.run(main())