import os, time, logging, sys, io
from datetime import datetime
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("pdf_uploader")

load_dotenv()
PDF_FILE_NAME = os.getenv("PDF_FILE_NAME", "fsnGuardiofourteen.pdf")
TARGET_URL = "https://www.amtha.org/application-form-organizations/"

def get_pdf_path():
    return os.path.abspath(PDF_FILE_NAME) if os.path.exists(PDF_FILE_NAME) else None

def upload_pdf_and_get_url(pdf_path):
    """Sirf PDF upload karo aur dynamic URL capture karo"""
    
    pdf_url = None
    
    with sync_playwright() as p:
        # Chrome launch
        context = p.chromium.launch_persistent_context(
            user_data_dir=os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "PDF_Upload_Profile"),
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
            ignore_default_args=["--enable-automation"],
            viewport={'width': 1366, 'height': 768}
        )
        page = context.new_page()
        
        # ============================================================
        # NETWORK INTERCEPT - CAPTURE PDF URL
        # ============================================================
        def capture_pdf_url(response):
            nonlocal pdf_url
            try:
                # Check for upload response
                if 'admin-ajax' in response.url and response.status == 200:
                    data = response.json()
                    if data and data.get('success') and data.get('data'):
                        file_data = data['data']
                        # Dynamic URL generate
                        if file_data.get('path') and file_data.get('file'):
                            # Direct URL
                            pdf_url = f"https://amtha.org/wp-content/uploads/wp_dndcf7_uploads/wpcf7-files/{file_data['path']}/{file_data['file']}"
                            logger.info(f"📄 PDF URL captured: {pdf_url}")
                        elif file_data.get('url'):
                            pdf_url = file_data['url']
                            logger.info(f"📄 PDF URL captured: {pdf_url}")
            except Exception as e:
                pass
        
        page.on("response", capture_pdf_url)
        
        logger.info("Navigating to form...")
        page.goto(TARGET_URL, timeout=30000)
        page.wait_for_selector('input[name="firstname"]', timeout=15000)
        time.sleep(2)
        
        # ============================================================
        # UPLOAD PDF
        # ============================================================
        logger.info("Uploading PDF...")
        file_input = page.locator('input[type="file"]').first
        file_input.set_input_files(pdf_path)
        time.sleep(5)  # Wait for upload to complete
        
        # ============================================================
        # TRY TO GET URL FROM HIDDEN INPUT
        # ============================================================
        if not pdf_url:
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
            if pdf_url:
                if not pdf_url.startswith('http'):
                    pdf_url = f"https://amtha.org/wp-content/uploads/wp_dndcf7_uploads/wpcf7-files/{pdf_url}"
                logger.info(f"📄 PDF URL from hidden input: {pdf_url}")
        
        # ============================================================
        # FINAL OUTPUT
        # ============================================================
        print("\n" + "="*70)
        print("PDF UPLOAD RESULT")
        print("="*70)
        print(f"PDF File: {os.path.basename(pdf_path)}")
        print(f"Dynamic PDF URL: {pdf_url if pdf_url else '❌ NOT FOUND'}")
        print("="*70 + "\n")
        
        # Save URL to file
        if pdf_url:
            with open("pdf_url.txt", "w") as f:
                f.write(pdf_url)
            logger.info(f"✅ URL saved to pdf_url.txt")
        
        # Wait for manual inspection
        logger.info("⏳ Waiting 30 seconds for manual inspection...")
        time.sleep(30)
        
        context.close()
        return pdf_url

def run():
    print("="*70)
    print("PDF UPLOAD - DYNAMIC URL CAPTURE")
    print("="*70 + "\n")
    
    pdf_path = get_pdf_path()
    if not pdf_path:
        logger.error(f"PDF not found: {PDF_FILE_NAME}")
        return
    
    logger.info(f"PDF: {pdf_path}")
    
    url = upload_pdf_and_get_url(pdf_path)
    
    if url:
        print(f"\n✅ Success! PDF URL: {url}")
    else:
        print("\n❌ Failed to capture PDF URL")

if __name__ == "__main__":
    run()