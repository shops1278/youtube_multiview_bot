import asyncio
import random
from playwright.async_api import async_playwright
import time

# Your embedded video URLs (iframe-safe)
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

    # Inject JS to mute, 2x speed, and set 144p
    await page.evaluate("""
        const player = document.querySelector('video');
        if (player) {
            player.muted = true;
            player.playbackRate = 2.0;
        }

        const qualityButton = () => {
            const settings = [...document.querySelectorAll('button')].find(b => b.title?.includes('Settings'));
            if (settings) settings.click();
        };
        setTimeout(qualityButton, 3000);
    """)

    print(f"✅ Profile {profile_num + 1} playing: {url}")
    await page.wait_for_timeout(180000)  # 3 minutes
    await context.close()
    await browser.close()

async def main_loop():
    while True:
        async with async_playwright() as playwright:
            tasks = []
            for i, url in enumerate(VIDEO_URLS):
                tasks.append(play_video(playwright, url, i))
            await asyncio.gather(*tasks)
            print("🔁 Restarting loop with new profiles...\n")
            await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main_loop())
