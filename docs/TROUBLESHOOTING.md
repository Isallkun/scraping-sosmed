# Troubleshooting Guide - Instagram Scraper

## Common Issues and Solutions

### 1. Authentication Timeout

**Symptoms:**
```
ERROR - Authentication timeout: Message: ...
TimeoutException: Message:
```

**Causes:**
- Instagram page loading slowly
- Selectors changed (Instagram updates their UI)
- Network issues
- Instagram detecting automation

**Solutions:**

#### Solution A: Increase Timeout
Edit `.env`:
```env
SCRAPER_TIMEOUT=900  # Increase to 15 minutes
```

#### Solution B: Manual Login First
1. Open Chrome manually
2. Go to instagram.com
3. Login with your account
4. Keep browser open
5. Run scraper (it may reuse session)

#### Solution C: Check Credentials
```bash
# Verify credentials in .env
SCRAPER_USERNAME=your_actual_username
SCRAPER_PASSWORD=your_actual_password
```

#### Solution D: Disable 2FA
Instagram 2FA (Two-Factor Authentication) will block automated login:
1. Go to Instagram Settings
2. Security → Two-Factor Authentication
3. Temporarily disable it
4. Run scraper
5. Re-enable after scraping

### 2. Instagram Detecting Bot

**Symptoms:**
- "Suspicious Login Attempt" message
- CAPTCHA appears
- Account temporarily locked
- Login works manually but not with scraper

**Solutions:**

#### Solution A: Use Demo Mode
```bash
python demo_scraper.py
```
This generates sample data without real scraping.

#### Solution B: Lower Rate Limit
Edit `.env`:
```env
SCRAPER_RATE_LIMIT=10  # Very slow, but safer
```

#### Solution C: Add Delays
Wait between scraping sessions:
```bash
# Scrape, then wait 1 hour before next scrape
python scrape_instagram.py
# Wait...
python scrape_instagram.py
```

#### Solution D: Use Residential Proxy
Instagram is less likely to block residential IPs:
```python
# Add proxy configuration (advanced)
proxy = "http://username:password@proxy-server:port"
```

### 3. Element Not Found

**Symptoms:**
```
NoSuchElementException: Message: no such element
```

**Causes:**
- Instagram changed their HTML structure
- Page not fully loaded
- Different language/region

**Solutions:**

#### Solution A: Update Selectors
Instagram frequently changes their UI. Check `scraper/scrapers/instagram.py`:
```python
SELECTORS = {
    'username_input': 'input[name="username"]',  # May need update
    'password_input': 'input[name="password"]',  # May need update
    # ...
}
```

#### Solution B: Inspect Page Manually
1. Open Instagram in Chrome
2. Right-click → Inspect
3. Find the actual selectors
4. Update SELECTORS in code

### 4. ChromeDriver Issues

**Symptoms:**
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```

**Solutions:**

#### Solution A: Install ChromeDriver
```bash
# Windows (using chocolatey)
choco install chromedriver

# Or download manually from:
# https://chromedriver.chromium.org/
```

#### Solution B: Check Chrome Version
```bash
# Chrome and ChromeDriver versions must match
chrome --version
chromedriver --version
```

#### Solution C: Update Selenium
```bash
pip install --upgrade selenium
```

### 5. Rate Limiting / IP Blocking

**Symptoms:**
- Slow responses
- Frequent errors
- "Too many requests" messages
- Temporary account restrictions

**Solutions:**

#### Solution A: Respect Rate Limits
```env
SCRAPER_RATE_LIMIT=15  # Slower = safer
```

#### Solution B: Scrape Less Frequently
```bash
# Instead of scraping every hour, scrape once per day
# Use cron or Task Scheduler
```

#### Solution C: Use Multiple Accounts
Rotate between different Instagram accounts (be careful with TOS).

### 6. Credentials Not Working

**Symptoms:**
```
ERROR - Login failed - credentials may be incorrect
```

**Solutions:**

#### Solution A: Verify Credentials
1. Try logging in manually at instagram.com
2. Check for typos in `.env` file
3. Ensure no extra spaces

#### Solution B: Check Special Characters
If password contains special characters:
```env
# Use quotes if password has special chars
SCRAPER_PASSWORD="p@ssw0rd!123"
```

#### Solution C: Reset Password
1. Reset Instagram password
2. Update `.env` file
3. Try again

### 7. Headless Mode Issues

**Symptoms:**
- Works with `--no-headless` but fails with `--headless`
- Different behavior in headless mode

**Solutions:**

#### Solution A: Always Use Non-Headless for Debugging
```bash
python scrape_instagram.py URL 5 false
```

#### Solution B: Add Headless-Specific Options
Some sites detect headless mode. Add more options to appear like real browser.

### 8. Memory / Performance Issues

**Symptoms:**
- Browser crashes
- System slowdown
- Out of memory errors

**Solutions:**

#### Solution A: Limit Posts
```bash
# Scrape fewer posts at a time
python scrape_instagram.py URL 10 false  # Instead of 100
```

#### Solution B: Close Other Applications
Free up system resources before scraping.

#### Solution C: Use Headless Mode
```bash
# Headless uses less memory
python scrape_instagram.py URL 50 true
```

## Debugging Steps

### Step 1: Check Logs
```bash
# View latest logs
type logs\scraper.instagram.log
```

### Step 2: Run with Debug Logging
```bash
python -m scraper.main_scraper \
  --target URL \
  --limit 3 \
  --no-headless \
  --log-level DEBUG
```

### Step 3: Test with Demo Mode
```bash
# Verify sentiment analysis works
python demo_scraper.py
python -m sentiment.main_analyzer --input output/demo_*.json --output output/demo_*_sentiment.json
```

### Step 4: Manual Browser Test
1. Open Chrome
2. Go to instagram.com
3. Try logging in manually
4. Check if account works

### Step 5: Check Network
```bash
# Test Instagram connectivity
ping instagram.com
```

## Alternative Approaches

### Approach 1: Use Instagram API (Official)
- More reliable
- No bot detection
- Requires API approval
- Limited features

### Approach 2: Use Third-Party Services
- Apify
- Bright Data
- ScraperAPI
- More expensive but more reliable

### Approach 3: Manual Export
1. Use Instagram's "Download Your Data" feature
2. Export posts manually
3. Process with sentiment analyzer

## Prevention Tips

### Tip 1: Start Small
Always test with `--limit 3` first before scaling up.

### Tip 2: Monitor Logs
Check `logs/` directory regularly for warnings.

### Tip 3: Respect Rate Limits
Don't scrape too frequently. Instagram will notice.

### Tip 4: Use Demo Mode for Development
Develop and test features with demo data first.

### Tip 5: Keep Credentials Secure
Never commit `.env` file to version control.

## Getting Help

### Check Documentation
- `README.md` - Main documentation
- `USAGE_GUIDE.md` - Usage examples
- `QUICKSTART.md` - Quick start guide

### Check Logs
```bash
# Instagram scraper logs
type logs\scraper.instagram.log

# Sentiment analyzer logs
type logs\sentiment.log
```

### Run Tests
```bash
# Verify system is working
python -m pytest tests/ -v
```

### Contact Support
If issues persist:
1. Collect error messages
2. Check logs
3. Try demo mode
4. Report issue with details

## FAQ

**Q: Why does scraping take so long?**
A: Instagram has anti-bot measures. We add delays to appear human-like.

**Q: Can I scrape without logging in?**
A: No, Instagram requires authentication for most content.

**Q: Is this legal?**
A: Check Instagram's Terms of Service. Use responsibly and ethically.

**Q: Why does it work sometimes but not others?**
A: Instagram's anti-bot detection varies. Try different times of day.

**Q: Can I scrape private accounts?**
A: Only if you're following them and logged in.

**Q: How many posts can I scrape?**
A: Start with 10-50. More than 100 may trigger rate limiting.

**Q: Does this work with Twitter/Facebook?**
A: Yes, but they have similar anti-bot measures.

---

**Remember**: Always respect platform Terms of Service and use responsibly! 🙏
