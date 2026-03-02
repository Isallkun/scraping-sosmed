"""
Test Facebook Login - Debug Script

Script sederhana untuk test login Facebook dan debug masalah autentikasi.
"""

import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load environment variables
load_dotenv()

def test_facebook_login():
    """Test Facebook login dengan debug output."""
    
    # Get credentials
    username = os.getenv('FACEBOOK_USERNAME')
    password = os.getenv('FACEBOOK_PASSWORD')
    
    if not username or not password:
        print("❌ Error: Facebook credentials not found in .env file")
        return
    
    print(f"🔐 Testing Facebook login...")
    print(f"   Username: {username}")
    print(f"   Password: {'*' * len(password)}")
    print()
    
    # Setup Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Run with visible browser for debugging
    # options.add_argument('--headless')
    
    driver = webdriver.Chrome(options=options)
    driver.set_window_size(1600, 900)
    
    try:
        # Navigate to Facebook login
        print("📱 Navigating to Facebook login page...")
        driver.get("https://www.facebook.com/login")
        time.sleep(3)
        
        print(f"   Current URL: {driver.current_url}")
        print(f"   Page title: {driver.title}")
        print()
        
        # Try to find email input with multiple selectors
        print("🔍 Looking for email input field...")
        email_selectors = [
            'input[name="email"]',
            'input[id="email"]',
            'input[type="text"]',
            '#email'
        ]
        
        email_input = None
        for selector in email_selectors:
            try:
                email_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"   ✅ Found email input with selector: {selector}")
                break
            except NoSuchElementException:
                print(f"   ❌ Not found with selector: {selector}")
        
        if not email_input:
            print("❌ Could not find email input field!")
            print("📸 Taking screenshot...")
            driver.save_screenshot("facebook_login_page.png")
            print("   Screenshot saved: facebook_login_page.png")
            return
        
        print()
        
        # Try to find password input
        print("🔍 Looking for password input field...")
        password_selectors = [
            'input[name="pass"]',
            'input[id="pass"]',
            'input[type="password"]',
            '#pass'
        ]
        
        password_input = None
        for selector in password_selectors:
            try:
                password_input = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"   ✅ Found password input with selector: {selector}")
                break
            except NoSuchElementException:
                print(f"   ❌ Not found with selector: {selector}")
        
        if not password_input:
            print("❌ Could not find password input field!")
            return
        
        print()
        
        # Enter credentials
        print("⌨️  Entering credentials...")
        email_input.clear()
        email_input.send_keys(username)
        time.sleep(1)
        
        password_input.clear()
        password_input.send_keys(password)
        time.sleep(1)
        
        print("   ✅ Credentials entered")
        print()
        
        # Find and click login button
        print("🔍 Looking for login button...")
        login_selectors = [
            'button[name="login"]',
            'button[type="submit"]',
            'input[type="submit"]',
            'button[data-testid="royal_login_button"]'
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                login_button = driver.find_element(By.CSS_SELECTOR, selector)
                print(f"   ✅ Found login button with selector: {selector}")
                break
            except NoSuchElementException:
                print(f"   ❌ Not found with selector: {selector}")
        
        if not login_button:
            print("❌ Could not find login button!")
            return
        
        print()
        print("🚀 Clicking login button...")
        login_button.click()
        
        # Wait for navigation
        print("⏳ Waiting for login to complete...")
        time.sleep(5)
        
        current_url = driver.current_url
        print(f"   Current URL after login: {current_url}")
        print(f"   Page title: {driver.title}")
        print()
        
        # Check if login was successful
        if 'login' in current_url.lower():
            print("❌ Login FAILED - Still on login page")
            print()
            
            # Check for error messages
            print("🔍 Looking for error messages...")
            try:
                error_elements = driver.find_elements(By.CSS_SELECTOR, '[role="alert"], .error, ._9ay7')
                if error_elements:
                    for elem in error_elements:
                        error_text = elem.text.strip()
                        if error_text:
                            print(f"   ⚠️  Error message: {error_text}")
                else:
                    print("   No error messages found")
            except Exception as e:
                print(f"   Could not check for errors: {e}")
            
            print()
            print("📸 Taking screenshot of login failure...")
            driver.save_screenshot("facebook_login_failed.png")
            print("   Screenshot saved: facebook_login_failed.png")
            
        else:
            print("✅ Login SUCCESSFUL!")
            print(f"   Redirected to: {current_url}")
            
            print()
            print("📸 Taking screenshot of successful login...")
            driver.save_screenshot("facebook_login_success.png")
            print("   Screenshot saved: facebook_login_success.png")
        
        # Keep browser open for inspection
        print()
        print("⏸️  Browser will stay open for 10 seconds for inspection...")
        time.sleep(10)
        
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        
        print()
        print("📸 Taking screenshot of error state...")
        driver.save_screenshot("facebook_error.png")
        print("   Screenshot saved: facebook_error.png")
    
    finally:
        print()
        print("🔒 Closing browser...")
        driver.quit()
        print("✅ Test complete!")


if __name__ == '__main__':
    test_facebook_login()
