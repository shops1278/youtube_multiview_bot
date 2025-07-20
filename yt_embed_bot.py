import asyncio
import random
import time
from playwright.async_api import async_playwright, TimeoutError, Error
from playwright._impl._errors import TargetClosedError

VIDEO_URLS = [
    "https://www.youtube.com/embed/u5BHEvPS1e4",
    "https://www.youtube.com/embed/7mENhao4cu8",
    "https://www.youtube.com/embed/kjKdfSk-Hcc",
    "https://www.youtube.com/embed/FfQl02H35gk",
    "https://www.youtube.com/embed/cdPkcwkfHIg"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)...",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X)...",
    "Mozilla/5.0 (X11; Linux x86_64)...",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64)...",
    "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X)..."
]

TIMEZONES = ["America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney", "Europe/Paris"]
LOCALES = ["en-US", "fr-FR", "ja-JP", "de-DE", "es-ES"]


async def play_video(playwright, url, profile_num):
    try:
        browser = await playwright.chromium.launch(
            headless=False,
            args=["--disable-gpu", "--no-sandbox", "--disable-dev-shm-usage"]
        )
        context = await browser.new_context(
            user_agent=USER_AGENTS[profile_num],
            locale=LOCALES[profile_num],
            timezone_id=TIMEZONES[profile_num],
            viewport={"width": 480, "height": 270}
        )
        page = await context.new_page()
        await page.goto(url, wait_until="domcontentloaded", timeout=60000)

        await page.wait_for_timeout(5000)

        await page.evaluate("""
            const video = document.querySelector('video');
            if (video) {
                video.muted = true;
                video.playbackRate = 2.0;
            }
        """)
        print(f"✅ Profile {profile_num+1} is playing: {url}")
        await page.wait_for_timeout(180000)  # 3 minutes
        await context.close()
        await browser.close()

    except TargetClosedError as e:
        print(f"⚠️ Browser closed unexpectedly in profile {profile_num+1}: {e}")
    except Exception as e:
        print(f"❌ General error in profile {profile_num+1}: {e}")


async def main_loop():
    while True:
        async with async_playwright() as playwright:
            tasks = []
            for i, url in enumerate(VIDEO_URLS):
                await asyncio.sleep(i * 5)  # slower stagger to reduce load
                tasks.append(play_video(playwright, url, i))
            await asyncio.gather(*tasks)
            print("🔁 Loop completed. Restarting with new profiles...\n")
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main_loop())
    except Exception as e:
        print(f"💥 Fatal error: {e}")
