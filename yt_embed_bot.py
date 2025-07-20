import asyncio
from playwright.async_api import async_playwright
import random
import time

YOUTUBE_LINKS = [
    "https://www.youtube.com/watch?v=u5BHEvPS1e4",
    "https://www.youtube.com/watch?v=7mENhao4cu8",
    "https://www.youtube.com/watch?v=kjKdfSk-Hcc",
    "https://www.youtube.com/watch?v=FfQl02H35gk",
    "https://www.youtube.com/watch?v=cdPkcwkfHIg",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:90.0) Gecko/20100101 Firefox/90.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 12_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.5481.77 Mobile Safari/537.36",
]

async def play_video(playwright, url, user_agent, index):
    try:
        browser = await playwright.chromium.launch(
            headless=False,
            args=[
                "--disable-gpu",
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-extensions",
                "--disable-infobars",
                "--disable-setuid-sandbox",
                "--disable-features=TranslateUI,BlinkGenPropertyTrees"
            ]
        )
        context = await browser.new_context(
            user_agent=user_agent,
            viewport={"width": 1280, "height": 720},
            locale="en-US"
        )
        page = await context.new_page()
        await page.goto(url)
        await page.wait_for_selector("video", timeout=15000)
        await page.evaluate("""
            const v = document.querySelector('video');
            if (v) {
                v.muted = true;
                v.playbackRate = 2.0;
                v.play();
            }
        """)
        await asyncio.sleep(30)  # Play for 30 seconds (2x = 1 minute simulated)
        await context.close()
        await browser.close()
    except Exception as e:
        print(f"[Tab {index}] Error: {e}")

async def main():
    async with async_playwright() as playwright:
        tasks = []
        for i in range(5):  # 5 tabs/profiles
            url = YOUTUBE_LINKS[i]
            user_agent = USER_AGENTS[i % len(USER_AGENTS)]
            tasks.append(play_video(playwright, url, user_agent, i + 1))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
