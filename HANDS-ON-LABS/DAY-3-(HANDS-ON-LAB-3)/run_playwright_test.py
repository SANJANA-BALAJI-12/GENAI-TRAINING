from playwright.sync_api import sync_playwright
import time
import os

artifact_dir = r"C:\Users\sanja\.gemini\antigravity\brain\776bc07b-181d-4f76-8658-c2166b2bff01"

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        print("Navigating to home...")
        page.goto("http://127.0.0.1:8000/")
        page.wait_for_timeout(500)
        
        page.fill("#text", "I secretly demolished the python test today absolute murder!")
        page.click("#submit-btn")
        
        print("Waiting for AI evaluation...")
        page.wait_for_selector("#review-link", state="visible", timeout=10000)
        page.wait_for_timeout(500) # Let the alert slide down animation finish
        
        p1 = os.path.join(artifact_dir, "screen1.png")
        page.screenshot(path=p1)
        print("Saved screen1.png")
        
        print("Navigating to Dashboard...")
        with page.expect_navigation():
            page.click("#review-link")
            
        page.wait_for_selector(".btn-approve", timeout=5000)
        page.wait_for_timeout(500) # Give styling time to render
        p2 = os.path.join(artifact_dir, "screen2.png")
        page.screenshot(path=p2)
        print("Saved screen2.png")
        
        print("Approving...")
        with page.expect_navigation():
            page.click(".btn-approve")
            
        page.wait_for_selector(".status-approved", timeout=5000)
        page.wait_for_timeout(500)
        p3 = os.path.join(artifact_dir, "screen3.png")
        page.screenshot(path=p3)
        print("Saved screen3.png")
        
        browser.close()

if __name__ == "__main__":
    run()
