import asyncio
from playwright.async_api import async_playwright
import random
from fake_useragent import UserAgent

# Your video URLs
video_urls = [
    "https://youtu.be/cdPkcwkfHIg",
    "https://youtu.be/kjKdfSk-Hcc",
    "https://youtu.be/FfQl02H35gk"
]

# Optional: proxies in format "http://username:password@host:port"
proxies = [
    None,  # No proxy
    # "http://user:pass@ip:port",
]

# Watch duration (seconds)
WATCH_TIME = 60 * 5  # 5 minutes

# Start browser context
async def view_video(playwright, url, proxy=None):
    try:
        chromium = playwright.chromium
        args = [
            "--disable-extensions",
            "--disable-blink-features=AutomationControlled",
            "--mute-audio",
        ]

        ua = UserAgent().random

        browser = await chromium.launch(
            headless=True,
            args=args,
            proxy={"server": proxy} if proxy else None
        )

        context = await browser.new_context(
            user_agent=ua,
            locale=random.choice(["en-US", "de-DE", "fr-FR", "it-IT", "es-ES"]),
            viewport={"width": 1280, "height": 720}
        )

        page = await context.new_page()
        print(f"🎬 Opening {url}")
        await page.goto(url, timeout=60000)

        # Wait for YouTube to load
        await page.keyboard.press("k")  # Simulate play (toggle)
        await page.wait_for_timeout(3000)

        # Set lowest quality via keyboard (3 times ↓, once Enter)
        await page.keyboard.press("Shift+>")
        await page.keyboard.press("Shift+>")
        await page.wait_for_timeout(500)
        await page.keyboard.press("s")  # Open settings
        await page.wait_for_timeout(500)
        for _ in range(3):
            await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")

        print(f"✅ Playing: {url}")
        await page.wait_for_timeout(WATCH_TIME * 1000)

        await context.close()
        await browser.close()
    except Exception as e:
        print(f"❌ Error with {url}: {e}")

async def main():
    async with async_playwright() as p:
        tasks = []
        for i in range(3):  # Open 3 videos
            url = random.choice(video_urls)
            proxy = random.choice(proxies)
            tasks.append(view_video(p, url, proxy))
        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
