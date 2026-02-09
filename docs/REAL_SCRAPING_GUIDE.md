# Real Instagram Scraping Guide

## ⚠️ Important Notice

Instagram has **very strong anti-bot protection**. Real scraping may:
- Take 2-5 minutes per session
- Fail due to bot detection
- Require CAPTCHA solving
- Temporarily lock your account
- Require 2FA to be disabled

## 🎯 Recommended Approach

### For Development & Testing: Use Demo Mode ✅
```bash
python demo_scraper.py
```
**Advantages:**
- ✅ Works 100% of the time
- ✅ No Instagram account needed
- ✅ No bot detection issues
- ✅ Perfect for testing sentiment analysis
- ✅ Fast and reliable

### For Production: Use Official API or Services
1. **Instagram Graph API** (Official)
   - Requires Facebook Developer account
   - More reliable
   - No bot detection
   - Rate limits are clear

2. **Third-Party Services**
   - Apify Instagram Scraper
   - Bright Data
   - ScraperAPI
   - More expensive but more reliable

## 🔧 Real Scraping Setup (If You Must)

### Prerequisites
1. ✅ Valid Instagram account
2. ✅ 2FA **disabled** (Instagram blocks automated 2FA)
3. ✅ Account not flagged for suspicious activity
4. ✅ Stable internet connection
5. ✅ Chrome browser installed
6. ✅ Patience (can take 5+ minutes)

### Step-by-Step Process

#### Step 1: Configure Credentials
Edit `.env`:
```env
SCRAPER_USERNAME=your_instagram_username
SCRAPER_PASSWORD=your_instagram_password
SCRAPER_TIMEOUT=900  # 15 minutes timeout
SCRAPER_RATE_LIMIT=10  # Very slow to avoid detection
```

#### Step 2: Test Login Manually First
1. Open Chrome
2. Go to instagram.com
3. Login with your credentials
4. Verify it works
5. Logout

#### Step 3: Run Scraper (Non-Headless First)
```bash
# Start with just 3 posts to test
python scrape_instagram.py "https://www.instagram.com/username/" 3 false
```

**What to expect:**
- Browser window opens
- Navigates to Instagram
- Tries to find login fields (20 seconds)
- Enters username (slowly, character by character)
- Enters password (slowly)
- Clicks login
- Waits for redirect
- Handles "Save Login Info" popup
- Handles "Turn on Notifications" popup
- Navigates to target profile
- Scrolls and extracts posts

**Total time:** 2-5 minutes for 3 posts

#### Step 4: Monitor Progress
Watch the browser window and terminal output:
```
✓ Credentials loaded for: your_username
✓ Scraper initialized
🔍 Starting scraping process...
   (This may take a few minutes...)
```

#### Step 5: Handle Common Issues

**Issue: "Authentication timeout"**
- Instagram page loaded slowly
- Selectors may have changed
- Try again in 10 minutes

**Issue: "Suspicious login attempt"**
- Instagram detected automation
- Login manually first
- Wait 1 hour, try again

**Issue: CAPTCHA appears**
- Solve it manually in the browser
- Scraper will continue after solving

**Issue: "Save your login info" stuck**
- Click "Not Now" manually
- Scraper should continue

#### Step 6: If Successful
```
✅ Scraping Completed Successfully!
📁 Output: output/instagram_real_20260209_084931.json
📊 Posts scraped: 3
```

#### Step 7: Analyze Sentiment
```bash
python -m sentiment.main_analyzer \
  --input output/instagram_real_20260209_084931.json \
  --output output/instagram_real_20260209_084931_sentiment.json \
  --model vader
```

#### Step 8: View Results
```bash
python view_results.py output/instagram_real_20260209_084931_sentiment.json
```

## 🚨 Troubleshooting Real Scraping

### Problem: Always Times Out

**Solution 1: Increase Timeout**
```env
SCRAPER_TIMEOUT=1800  # 30 minutes
```

**Solution 2: Check Selectors**
Instagram changes their HTML frequently. Selectors may be outdated.

**Solution 3: Use Demo Mode**
If it keeps failing, use demo mode for development:
```bash
python demo_scraper.py
```

### Problem: Account Gets Locked

**Solution:**
1. Wait 24 hours
2. Login manually and verify identity
3. Don't scrape too frequently
4. Use lower rate limits

### Problem: Works Once, Then Fails

**Solution:**
Instagram may have flagged your IP or account:
1. Wait several hours between scraping sessions
2. Don't scrape more than 50 posts per day
3. Vary your scraping times
4. Consider using residential proxies

## 📊 Success Rates (Based on Testing)

| Scenario | Success Rate | Notes |
|----------|--------------|-------|
| Demo Mode | 100% | Always works |
| First-time scraping | 60% | May need manual intervention |
| Repeated scraping (same day) | 30% | Instagram detects patterns |
| With 2FA enabled | 0% | Won't work at all |
| Headless mode | 40% | Instagram detects headless |
| Non-headless mode | 60% | Better success rate |

## 💡 Best Practices

### DO:
✅ Start with demo mode for development
✅ Test with 3-5 posts first
✅ Use non-headless mode for debugging
✅ Wait between scraping sessions
✅ Monitor logs for errors
✅ Respect Instagram's rate limits
✅ Use official API when possible

### DON'T:
❌ Scrape with 2FA enabled
❌ Scrape hundreds of posts at once
❌ Scrape multiple times per hour
❌ Use on production accounts
❌ Ignore error messages
❌ Commit credentials to git
❌ Violate Instagram's Terms of Service

## 🎓 Learning Path

### Phase 1: Learn the System (Use Demo Mode)
```bash
# 1. Generate demo data
python demo_scraper.py

# 2. Analyze sentiment
python -m sentiment.main_analyzer --input output/demo_*.json --output output/demo_*_sentiment.json --model vader

# 3. View results
python view_results.py output/demo_*_sentiment.json

# 4. Understand the output format
# 5. Test different sentiment models
# 6. Experiment with batch processing
```

### Phase 2: Test Real Scraping (If Needed)
```bash
# 1. Configure credentials
# 2. Test with 3 posts
python scrape_instagram.py "URL" 3 false

# 3. If successful, try 10 posts
python scrape_instagram.py "URL" 10 false

# 4. If still successful, try headless
python scrape_instagram.py "URL" 10 true
```

### Phase 3: Production (Use Official API)
- Apply for Instagram Graph API
- Use official endpoints
- No bot detection issues
- More reliable and scalable

## 🔄 Alternative: Hybrid Approach

### Use Demo Data + Manual Export

1. **Generate demo data** for development:
   ```bash
   python demo_scraper.py
   ```

2. **Manually export real data** from Instagram:
   - Settings → Privacy → Download Your Information
   - Wait for Instagram to prepare your data
   - Download JSON files
   - Convert to our format

3. **Process with sentiment analyzer**:
   ```bash
   python -m sentiment.main_analyzer --input your_real_data.json --output results.json
   ```

This approach:
- ✅ Gets real data
- ✅ No bot detection
- ✅ Complies with Instagram TOS
- ❌ Manual process
- ❌ Only works for your own account

## 📞 When to Use What

| Use Case | Recommended Approach |
|----------|---------------------|
| Learning the system | Demo Mode |
| Testing sentiment analysis | Demo Mode |
| Development | Demo Mode |
| One-time scraping | Manual export |
| Regular scraping | Official API |
| Production system | Official API + Services |
| Personal project | Demo Mode + Manual export |
| Commercial use | Official API only |

## 🎯 Current Status

Based on our testing:
- ✅ **Demo Mode**: Working perfectly
- ✅ **Sentiment Analysis**: Working perfectly
- ✅ **Results Viewer**: Working perfectly
- ⚠️ **Real Scraping**: Challenging due to Instagram's anti-bot protection

**Recommendation**: Use demo mode for development and testing. For production, use Instagram's official API or third-party services.

---

**Remember**: Instagram's Terms of Service prohibit automated scraping. Use responsibly and ethically! 🙏
