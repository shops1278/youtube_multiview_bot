import asyncio
from playwright.async_api import async_playwright, TimeoutError, Error

VIDEO_URLS = [
    "https://www.youtube.com/embed/u5BHEvPS1e4",
    "https://www.youtube.com/embed/7mENhao4cu8",
    "https://www.youtube.com/embed/kjKdfSk-Hcc",
    "https://www.youtube.com/embed/FfQl02H35gk",
    "https://www.youtube.com/embed/cdPkcwkfHIg"
]

async def play_video(context, url):
    try:
        page = await context.new_page()
        await page.goto(url, timeout=60000)
        await page.wait_for_selector("video", timeout=20000)

        # Mute video
        await page.evaluate("document.querySelector('video').muted = true")

        # Set playback speed to 2x
        await page.evaluate("document.querySelector('video').playbackRate = 2.0")

        # Try to set quality to 144p via keyboard shortcut (might not work in all embeds)
        await page.keyboard.press("Shift+>")
        await asyncio.sleep(2)

        print(f"✅ Playing: {url}")
        await asyncio.sleep(1800)  # Play for 30 mins

        await page.close()
    except TimeoutError:
        print(f"⛔ Timeout loading: {url}")
    except Error as e:
        print(f"⚠️ Playwright error: {e}")
    except Exception as ex:
        print(f"‼️ Unexpected error: {ex}")

async def run_bot():
    while True:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=False, args=["--start-maximized"])
            tasks = []

            for url in VIDEO_URLS:
                context = await browser.new_context()
                tasks.append(play_video(context, url))

            await asyncio.gather(*tasks)
            await browser.close()

if __name__ == "__main__":
    asyncio.run(run_bot())
