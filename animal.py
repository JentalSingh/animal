import os
import time
import random
import string
import logging
import requests
from datetime import datetime
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha

try:
    import winreg
except ImportError:
    winreg = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("amthaAutomation")

if os.path.exists(".env"):
    load_dotenv(".env")

CAPTCHA_API_KEY = os.getenv("TWOCAPTCHA_API_KEY", "YOUR_API_KEY")
PDF_FILE_NAME = os.getenv("PDF_FILE_NAME", "fsnGuardiofourteen.pdf")
TARGET_URL = "https://www.amtha.org/application-form-organizations/"
REAL_SITEKEY = "6Lc11OQlAAAAACmAeYFlvS0U2bIgPiSC_xV9wJfU"

SCREENSHOT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)

def find_chrome_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
        path = winreg.QueryValue(key, None)
        winreg.CloseKey(key)
        if path and os.path.exists(path): return path
    except: pass
    
    for path in ["C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe", 
                 "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
                 os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"]:
        if os.path.exists(path): return path
    return None

def get_residential_proxies():
    for fname in ["Webshare proxies.txt", "Webshare proxies", "proxies.txt"]:
        if os.path.exists(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []

def test_proxy(proxy):
    parts = proxy.strip().split(":")
    f_proxy = f"http://{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}" if len(parts) == 4 else (proxy if proxy.startswith("http") else f"http://{proxy}")
    try:
        return requests.get("https://httpbin.org/ip", proxies={"http": f_proxy, "https": f_proxy}, timeout=5).status_code == 200
    except: return False

def generate_random_data():
    first = random.choice(["gfthyjuioh", "Mike", "David", "Chris", "James", "John"])
    last = random.choice(["lkhvjo", "Brown", "Jones", "Miller", "Davis", "Smith"])
    unique = ''.join(random.choices(string.digits, k=4))
    return first, last, f"gcfghjkh{unique}@gmail.com", f"9876543{random.randint(10,99)}", "dxfcgvhnb", "fghukyh_tbf"

def submit_form(proxy_str, pdf_path, first, last, email, phone, org_name, eq1_name):
    p_proxy = None
    if proxy_str:
        cleaned = proxy_str.replace("http://", "").replace("https://", "").split(":")
        if len(cleaned) == 4:
            p_proxy = {"server": f"http://{cleaned[0]}:{cleaned[1]}", "username": cleaned[2], "password": cleaned[3]}

    chrome_path = find_chrome_path()
    profile = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "AutomationProfile")
    os.makedirs(profile, exist_ok=True)
    
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        context = None
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=profile, executable_path=chrome_path, headless=False, proxy=p_proxy,
                args=["--disable-blink-features=AutomationControlled"], ignore_default_args=["--enable-automation"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={'width': 1366, 'height': 768}
            )
            page = context.new_page()
            logger.info("🌐 Navigating to form...")
            page.goto(TARGET_URL, wait_until="commit", timeout=25000)
            page.wait_for_selector('input[name="firstname"]', state="visible", timeout=10000)
            time.sleep(3)
            
            # --- SAFE JS INJECTION ENGINE ---
            logger.info("📝 Injecting fields into the DOM...")
            js_code = f"""
                (function() {{
                    function fillInput(name, value) {{
                        let el = document.querySelector(`input[name="${{name}}"], textarea[name="${{name}}"], select[name="${{name}}"]`);
                        if (el) {{
                            el.value = value;
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            return true;
                        }}
                        return false;
                    }}
                    
                    fillInput('firstname', '{first}');
                    fillInput('lastname', '{last}');
                    fillInput('age', '23');
                    fillInput('youremail', '{email}');
                    fillInput('email', '{email}');
                    fillInput('confirmemail', '{email}');
                    fillInput('tel', '{phone}');
                    fillInput('phone', '{phone}');
                    fillInput('address', 'ertyuyf456');
                    fillInput('city', 'cghj');
                    fillInput('state', 'fghjgh');
                    fillInput('zip', '34567');
                    fillInput('zipcode', '34567');
                    fillInput('farm', '{org_name}');
                    fillInput('organization', '{org_name}');
                    fillInput('currently', 'Yes');
                    fillInput('handlers8', 'Yes');
                    fillInput('owned', 'Yes');
                    fillInput('explain', 'All equines are owned by the primary handler');
                    fillInput('type1', 'Miniature Horse');
                    fillInput('horseage1', '2');
                    fillInput('name1', '{eq1_name}');
                    fillInput('equines7', 'Yes');
                }})();
            """
            page.evaluate(js_code)
            time.sleep(2)
            
            if os.path.exists(pdf_path):
                page.locator('input[type="file"]').first.set_input_files(pdf_path)
                logger.info("📁 PDF attached successfully.")

            # ============================================================
            # ⏳ LIVE EYE-CHECK DELAY (2 MINUTE TIMER)
            # ============================================================
            logger.info("⏳ Data fill ho gaya hai! Form check karne ke liye browser 2 minutes tak ruka hua hai...")
            time.sleep(120) 
            # ============================================================

            # --- Captcha Logic ---
            logger.info("🔐 Requesting Captcha Matrix...")
            solver = TwoCaptcha(CAPTCHA_API_KEY)
            try:
                result = solver.recaptcha(sitekey=REAL_SITEKEY, url=TARGET_URL)
                token = result.get('code')
                if token:
                    page.evaluate(f"""
                        (token) => {{
                            let t1 = document.getElementById('g-recaptcha-response'); if(t1) t1.value = token;
                            let t2 = document.querySelector('textarea[name="g-recaptcha-response"]');
                            if(t2) {{ t2.value = token; t2.dispatchEvent(new Event('change', {{bubbles:true}})); }}
                        }}
                    """, token)
            except Exception as ce: logger.error(f"Captcha matrix failed: {ce}")

            # --- Original Multiple Submission Click System ---
            submit_btn = page.locator('input[type="submit"], button:has-text("SEND")').first
            submission_status = None
            
            for i in range(5):
                logger.info(f"🚀 Submit click #{i+1}")
                submit_btn.click()
                time.sleep(3)
                current_url = page.url.lower()
                
                if any(x in current_url for x in ["payment", "checkout", "thank", "success"]):
                    submission_status = 'mail_sent'
                    break

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            page.screenshot(path=os.path.join(SCREENSHOT_FOLDER, f"final_{ts}.png"))
            context.close()
            return {'submission_status': submission_status, 'email': email}, "success"
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            if context: context.close()
            return None, "error"

def run_bot():
    if not os.path.exists(PDF_FILE_NAME):
        logger.error(f"❌ PDF Pack missing: {PDF_FILE_NAME}")
        return
    
    proxies = get_residential_proxies() or [None]
    random.shuffle(proxies)
    
    for attempt, proxy in enumerate(proxies[:10], 1):
        if proxy and not test_proxy(proxy): continue
        print(f"\n🔄 Running Attempt #{attempt}")
        
        first, last, email, phone, org_name, eq1_name = generate_random_data()
        result, status = submit_form(proxy, os.path.abspath(PDF_FILE_NAME), first, last, email, phone, org_name, eq1_name)
        
        if status == "success" and result and result.get('submission_status') == 'mail_sent':
            print(f"\n🎉 PIPELINE SUCCESS ON INSTANCE: {email}\n")
            break
        time.sleep(3)

if __name__ == "__main__":
    run_bot()