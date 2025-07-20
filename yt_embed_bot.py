import os
import asyncio
from playwright.async_api import async_playwright

# List of 5 YouTube embed links
urls = [
    "https://www.youtube.com/embed/u5BHEvPS1e4",
    "https://www.youtube.com/embed/7mENhao4cu8",
    "https://www.youtube.com/embed/kjKdfSk-Hcc",
    "https://www.youtube.com/embed/FfQl02H35gk",
    "https://www.youtube.com/embed/cdPkcwkfHIg"
]

# Ensure profile folders exist
for i in range(5):
    os.makedirs(f"user_data/profile_{i}", exist_ok=True)

async def main():
    async with async_playwright() as p:
        tasks = []
        for i, url in enumerate(urls):
            tasks.append(open_video(p, url, i))
        await asyncio.gather(*tasks)

async def open_video(p, url, profile_num):
    browser = await p.chromium.launch_persistent_context(
        user_data_dir=f"user_data/profile_{profile_num}",
        headless=False,
        args=[
            "--mute-audio",
            "--autoplay-policy=no-user-gesture-required",
            "--no-sandbox",
            "--disable-gpu"
        ]
    )
    page = await browser.new_page()
    try:
        await page.goto(url, timeout=60000)
        await page.wait_for_selector("video", timeout=15000)
        await page.evaluate("""
            () => {
                const video = document.querySelector("video");
                if (video) {
                    video.playbackRate = 2.0;
                    video.muted = true;
                    video.setAttribute("autoplay", "true");
                    video.setAttribute("playsinline", "true");
                    video.play().catch(() => {});
                }
            }
        """)
        print(f"[+] Video started: Profile {profile_num}")
        await asyncio.sleep(1800)  # Play for 30 minutes
    except Exception as e:
        print(f"[!] Error in profile {profile_num}: {e}")
    finally:
        await browser.close()

asyncio.run(main())
