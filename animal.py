import os, time, logging, sys, io, random
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pdf_uploader")

load_dotenv()
PDF_FILE_NAME = os.getenv("PDF_FILE_NAME", "fsnGuardiofourteen.pdf")
TARGET_URL = "https://www.amtha.org/application-form-organizations/"

# ============================================================
# REAL CHROME PATH
# ============================================================
def find_chrome_path():
    paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
    ]
    for path in paths:
        if os.path.exists(path):
            return path
    return None

# ============================================================
# PROXY FILE SE READ
# ============================================================
PROXY_FILE = "Webshare proxies.txt"

def load_proxies_from_file(filename=PROXY_FILE):
    proxies = []
    if os.path.exists(filename):
        with open(filename, "r", encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    parts = line.split(':')
                    if len(parts) == 4:
                        ip, port, username, password = parts
                        proxy = f"http://{username}:{password}@{ip}:{port}"
                        proxies.append(proxy)
                    else:
                        proxies.append(line)
        logger.info(f"✅ Loaded {len(proxies)} proxies from {filename}")
    else:
        logger.warning(f"⚠️ Proxy file not found: {filename}")
    return proxies

PROXY_LIST = load_proxies_from_file()

def get_pdf_path():
    return os.path.abspath(PDF_FILE_NAME) if os.path.exists(PDF_FILE_NAME) else None

def get_random_proxy():
    if PROXY_LIST:
        proxy = random.choice(PROXY_LIST)
        logger.info(f"🔄 Using proxy: {proxy[:40]}...")
        return proxy
    logger.warning("⚠️ No proxies available, running without proxy")
    return None

def upload_pdf_and_get_url(pdf_path):
    pdf_url = None
    proxy_str = get_random_proxy()
    chrome_path = find_chrome_path()
    
    proxy_config = None
    if proxy_str:
        try:
            if proxy_str.startswith('http'):
                parts = proxy_str.replace('http://', '').split('@')
                if len(parts) == 2:
                    auth, server = parts
                    user_pass = auth.split(':')
                    server_parts = server.split(':')
                    proxy_config = {
                        "server": f"http://{server}",
                        "username": user_pass[0],
                        "password": user_pass[1] if len(user_pass) > 1 else ''
                    }
                else:
                    proxy_config = {"server": proxy_str}
            elif proxy_str.startswith('socks5'):
                proxy_config = {"server": proxy_str}
        except Exception as e:
            logger.warning(f"Proxy parse error: {e}")
    
    with sync_playwright() as p:
        # ============================================================
        # REAL CHROME - BINA AUTOMATION FLAGS KE
        # ============================================================
        context_kwargs = {
            "user_data_dir": os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "Real_Profile"),
            "executable_path": chrome_path,
            "headless": False,
            "args": [
                "--no-first-run",
                "--no-default-browser-check",
                "--disable-infobars"
            ],
            "ignore_default_args": ["--enable-automation", "--disable-blink-features"],
            "viewport": {'width': 1366, 'height': 768}
        }
        
        if proxy_config:
            context_kwargs["proxy"] = proxy_config
            logger.info(f"🌐 Proxy configured: {proxy_config.get('server', 'unknown')}")
        
        context = p.chromium.launch_persistent_context(**context_kwargs)
        page = context.new_page()
        
        # ============================================================
        # NETWORK INTERCEPT - CAPTURE PDF URL
        # ============================================================
        def capture_pdf_url(response):
            nonlocal pdf_url
            try:
                if 'admin-ajax' in response.url and response.status == 200:
                    data = response.json()
                    if data and data.get('success') and data.get('data'):
                        file_data = data['data']
                        if file_data.get('path') and file_data.get('file'):
                            pdf_url = f"https://amtha.org/wp-content/uploads/wp_dndcf7_uploads/wpcf7-files/{file_data['path']}/{file_data['file']}"
                            logger.info(f"📄 PDF URL captured: {pdf_url}")
                        elif file_data.get('url'):
                            pdf_url = file_data['url']
                            logger.info(f"📄 PDF URL captured: {pdf_url}")
            except Exception as e:
                pass
        
        page.on("response", capture_pdf_url)
        
        logger.info("Navigating to form...")
        try:
            page.goto(TARGET_URL, timeout=30000)
            page.wait_for_selector('input[name="firstname"]', timeout=15000)
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            context.close()
            return None
        
        time.sleep(2)
        
        # ============================================================
        # UPLOAD PDF
        # ============================================================
        logger.info("Uploading PDF...")
        try:
            file_input = page.locator('input[type="file"]').first
            file_input.set_input_files(pdf_path)
            time.sleep(5)
            logger.info("PDF uploaded successfully!")
        except Exception as e:
            logger.error(f"Upload failed: {e}")
            context.close()
            return None
        
        # ============================================================
        # GET URL FROM HIDDEN INPUT
        # ============================================================
        if not pdf_url:
            try:
                pdf_url = page.evaluate("""
                    () => {
                        let url = null;
                        document.querySelectorAll('input[type="hidden"]').forEach(el => {
                            if (el.value && el.value.includes('.pdf')) {
                                url = el.value;
                            }
                        });
                        return url;
                    }
                """)
                if pdf_url and not pdf_url.startswith('http'):
                    pdf_url = f"https://amtha.org/wp-content/uploads/wp_dndcf7_uploads/wpcf7-files/{pdf_url}"
                    logger.info(f"📄 PDF URL from hidden input: {pdf_url}")
            except Exception as e:
                logger.warning(f"Could not get URL from hidden input: {e}")
        
        # ============================================================
        # FINAL OUTPUT
        # ============================================================
        print("\n" + "="*70)
        print("PDF UPLOAD RESULT")
        print("="*70)
        print(f"PDF File: {os.path.basename(pdf_path)}")
        print(f"Chrome: {chrome_path}")
        print(f"Proxy Used: {proxy_str[:40] + '...' if proxy_str else 'None'}")
        print(f"Dynamic PDF URL: {pdf_url if pdf_url else '❌ NOT FOUND'}")
        print("="*70 + "\n")
        
        if pdf_url:
            with open("pdf_url.txt", "w") as f:
                f.write(pdf_url)
            logger.info(f"✅ URL saved to pdf_url.txt")
        
        logger.info("⏳ Waiting 15 seconds...")
        time.sleep(15)
        
        context.close()
        return pdf_url

def run():
    print("="*70)
    print("PDF UPLOAD - REAL CHROME + WEBSHARE PROXY")
    print("="*70 + "\n")
    
    chrome_path = find_chrome_path()
    if chrome_path:
        logger.info(f"✅ Chrome found: {chrome_path}")
    else:
        logger.error("❌ Chrome not found!")
        return
    
    pdf_path = get_pdf_path()
    if not pdf_path:
        logger.error(f"PDF not found: {PDF_FILE_NAME}")
        return
    
    logger.info(f"PDF: {pdf_path}")
    logger.info(f"Available proxies: {len(PROXY_LIST)}")
    
    url = upload_pdf_and_get_url(pdf_path)
    
    if url:
        print(f"\n✅ Success! PDF URL: {url}")
    else:
        print("\n❌ Failed to capture PDF URL")

if __name__ == "__main__":
    run()