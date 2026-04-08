from playwright.sync_api import sync_playwright
import os

artifact_dir = r"C:\Users\sanja\.gemini\antigravity\brain\776bc07b-181d-4f76-8658-c2166b2bff01"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        job_url = "http://127.0.0.1:8000/moderate/4cfbadfa-2518-4f39-9960-d6f8d2176f60/review"
        print(f"Navigating to {job_url}")
        page.goto(job_url)
        page.wait_for_timeout(500)
        
        print("Clicking Authorize Payload...")
        with page.expect_navigation():
            page.click(".btn-approve")
            
        print("Waiting for resolved badge...")
        page.wait_for_selector(".status-approved", timeout=5000)
        page.wait_for_timeout(500)
        
        p3 = os.path.join(artifact_dir, "screen3.png")
        page.screenshot(path=p3)
        print("Saved screen3.png")
        
        browser.close()

if __name__ == "__main__":
    run()
