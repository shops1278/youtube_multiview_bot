import asyncio
import random
import time
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from playwright._impl._errors import TargetClosedError

VIDEO_URLS = [
    "https://www.youtube.com/embed/u5BHEvPS1e4",
    "https://www.youtube.com/embed/7mENhao4cu8",
    "https://www.youtube.com/embed/kjKdfSk-Hcc",
    "https://www.youtube.com/embed/FfQl02H35gk",
    "https://www.youtube.com/embed/cdPkcwkfHIg"
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPad; CPU OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1"
]

TIMEZONES = [
    "America/New_York", "Europe/London", "Asia/Tokyo", "Australia/Sydney", "Europe/Paris"
]

LOCALES = [
    "en-US", "fr-FR", "ja-JP", "de-DE", "es-ES"
]

async def play_video(playwright, url, profile_num):
    try:
        browser = await playwright.chromium.launch(headless=False)
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
            const player = document.querySelector('video');
            if (player) {
                player.muted = true;
                player.playbackRate = 2.0;
            }
        """)
        print(f"✅ Profile {profile_num + 1} playing: {url}")
        await page.wait_for_timeout(180000)  # 3 minutes
        await context.close()
        await browser.close()
    except (TargetClosedError, PlaywrightTimeoutError) as e:
        print(f"❌ Profile {profile_num + 1} crashed or closed early: {e}")
    except Exception as e:
        print(f"⚠️ Unexpected error (Profile {profile_num + 1}): {e}")

async def main_loop():
    while True:
        async with async_playwright() as playwright:
            tasks = []
            for i, url in enumerate(VIDEO_URLS):
                tasks.append(play_video(playwright, url, i))
                await asyncio.sleep(2)  # small delay to prevent overload
            await asyncio.gather(*tasks)
            print("🔁 Loop completed. Restarting...\n")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main_loop())
