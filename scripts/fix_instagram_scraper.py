# Patch untuk scrape_instagram_simple.py
# Menambahkan:
# 1. Skip pinned posts
# 2. Improved comment extraction

import re

# Fungsi untuk mendeteksi pinned post
def is_pinned_post(link_element):
    """Check if a post link is pinned"""
    try:
        # Cari parent article
        parent = link_element.find_element_by_xpath('./ancestor::article')
        # Cek SVG icon atau text yang menandakan pinned
        pinned_indicators = parent.find_elements_by_xpath(
            './/*[contains(@aria-label, "Pinned") or contains(@aria-label, "Disematkan")]'
        )
        return len(pinned_indicators) > 0
    except:
        return False

# Fungsi improved comment extraction
def extract_comments_improved(driver):
    """Extract comments with improved selectors for 2026 Instagram UI"""
    comments = []
    seen_texts = set()
    
    try:
        # Scroll untuk load comments
        driver.execute_script("window.scrollTo(0, 500);")
        time.sleep(2)
        
        # Coba berbagai selector untuk comment text
        selectors = [
            'ul ul li span',  # Nested list
            'div[role="button"] + div span',  # After button
            'h3 + div span',  # After username
        ]
        
        for selector in selectors:
            elements = driver.find_elements_by_css_selector(selector)
            
            for elem in elements:
                text = elem.text.strip()
                
                # Filter
                if not text or len(text) < 3:
                    continue
                if text in seen_texts:
                    continue
                    
                # Skip UI text
                ui_words = ['Reply', 'Balas', 'View', 'Lihat', 'Like', 'Suka']
                if any(word in text for word in ui_words):
                    continue
                
                seen_texts.add(text)
                comments.append({
                    'author': 'unknown',
                    'text': text,
                    'timestamp': datetime.now().isoformat() + 'Z'
                })
            
            if len(comments) > 0:
                break
                
    except Exception as e:
        print(f"Comment extraction error: {e}")
    
    return comments

print("Patch functions loaded. Apply manually to scrape_instagram_simple.py")
