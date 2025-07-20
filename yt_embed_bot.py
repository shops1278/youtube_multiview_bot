import asyncio
from playwright.async_api import async_playwright
import random
import time

VIDEO_URLS = [
    "https://www.youtube.com/embed/u5BHEvPS1e4",
    "https://www.youtube.com/embed/7mENhao4cu8",
    "https://www.youtube.com/embed/kjKdfSk-Hcc",
    "https://www.youtube.com/embed/FfQl02H35gk",
    "https://www.youtube.com/embed/cdPkcwkfHIg",
]

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/114.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 Chrome/113.0.0.0 Mobile Safari/537.36"
]

TIMEZONES = ["Europe/Berlin", "Asia/Karachi", "America/New_York", "Asia/Dubai", "Europe/London"]

async def play_video(playwright, profile_path, video_url, user_agent, timezone):
    browser = await playwright.chromium.launch_persistent_context(
        user_data_dir=profile_path,
        headless=False,
        locale="en-US",
        timezone_id=timezone,
        viewport={"width": 1280, "height": 720},
        args=["--mute-audio"],
    )
    page = await browser.new_page()
    await page.set_user_agent(user_agent)
    await page.goto(video_url)

    await page.wait_for_timeout(5000)  # wait for page to stabilize

    try:
        # Mute video
        await page.evaluate("document.querySelector('video').muted = true")

        # Set quality to 144p (low quality)
        await page.keyboard.press("f")  # full screen
        await page.mouse.click(1000, 500)
        await page.keyboard.press("m")  # mute again if needed
        await page.keyboard.press("Shift+>")  # speed up to 2x

        # Set playback speed
        await page.evaluate("document.querySelector('video').playbackRate = 2")

        # Get video duration and wait
        duration = await page.evaluate("document.querySelector('video').duration")
        await page.wait_for_timeout(int(duration * 1000 / 2))  # wait full duration at 2x speed

    except Exception as e:
        print(f"[ERROR] {video_url}: {e}")

    await browser.close()


async def main():
    async with async_playwright() as playwright:
        tasks = []

        for i, url in enumerate(VIDEO_URLS):
            profile_dir = f"user_data/profile_{i}"
            ua = USER_AGENTS[i % len(USER_AGENTS)]
            tz = TIMEZONES[i % len(TIMEZONES)]

            task = play_video(playwright, profile_dir, url, ua, tz)
            tasks.append(task)

        await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main())
