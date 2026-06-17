import os
import time
import random
import string
import logging
from datetime import datetime
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha

try:
    import winreg
except ImportError:
    winreg = None

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("amthaAutomation")

ENV_FILE_PATH = ".env"
if os.path.exists(ENV_FILE_PATH):
    load_dotenv(ENV_FILE_PATH)

CAPTCHA_API_KEY = os.getenv("TWOCAPTCHA_API_KEY", "YOUR_API_KEY")
PDF_FILE_NAME = os.getenv("PDF_FILE_NAME", "fsnGuardiofourteen.pdf")
TARGET_URL = "https://www.amtha.org/application-form-organizations/"
REAL_SITEKEY = "6Lc11OQlAAAAACmAeYFlvS0U2bIgPiSC_xV9wJfU"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCREENSHOT_FOLDER = os.path.join(SCRIPT_DIR, "screenshots")
os.makedirs(SCREENSHOT_FOLDER, exist_ok=True)


def find_chrome_path():
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe")
        path = winreg.QueryValue(key, None)
        winreg.CloseKey(key)
        if path and os.path.exists(path):
            return path
    except:
        pass
    
    common_paths = [
        "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
        "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
        os.path.expanduser("~") + "\\AppData\\Local\\Google\\Chrome\\Application\\chrome.exe"
    ]
    for path in common_paths:
        if os.path.exists(path):
            return path
    return None


def get_pdf_path():
    if os.path.exists(PDF_FILE_NAME):
        return os.path.abspath(PDF_FILE_NAME)
    if os.path.exists(PDF_FILE_NAME + ".pdf"):
        return os.path.abspath(PDF_FILE_NAME + ".pdf")
    return None


def generate_random_data():
    first_names = ["gfthyjuioh", "Mike", "David", "Chris", "James", "John"]
    last_names = ["lkhvjo", "Brown", "Jones", "Miller", "Davis", "Smith"]
    
    first = random.choice(first_names)
    last = random.choice(last_names)
    unique = ''.join(random.choices(string.digits, k=4))
    email = f"gcfghjkh{unique}@gmail.com"
    phone = f"9876543{random.randint(10,99)}"
    org_name = "dxfcgvhnb"
    
    eq1_name = "fghukyh_tbf"
    
    return first, last, email, phone, org_name, eq1_name


def submit_form(pdf_path, first, last, email, phone, org_name, eq1_name):
    chrome_path = find_chrome_path()
    
    automation_profile_dir = os.path.join(os.path.expanduser("~"), "AppData", "Local", "Google", "Chrome", "AutomationProfile")
    os.makedirs(automation_profile_dir, exist_ok=True)
    
    from playwright.sync_api import sync_playwright
    
    with sync_playwright() as p:
        context = None
        try:
            context = p.chromium.launch_persistent_context(
                user_data_dir=automation_profile_dir,
                executable_path=chrome_path,
                headless=False,
                args=["--disable-blink-features=AutomationControlled"],
                ignore_default_args=["--enable-automation"],
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
                viewport={'width': 1366, 'height': 768}
            )
            
            page = context.new_page()
            
            logger.info("🌐 Navigating to form...")
            page.goto(TARGET_URL, wait_until="commit", timeout=25000)
            page.wait_for_selector('input[name="firstname"]', state="visible", timeout=10000)
            time.sleep(3)
            
            # ============================================================
            # FILL ALL REQUIRED FIELDS - ALL DROPDOWNS = "YES"
            # ============================================================
            logger.info("📝 Filling required fields with ALL DROPDOWNS = YES...")
            
            js_code = f"""
                (function() {{
                    console.log("=== FILLING REQUIRED FIELDS ===");
                    
                    function fillInput(name, value) {{
                        let el = document.querySelector(`input[name="${{name}}"], textarea[name="${{name}}"]`);
                        if (el) {{
                            el.value = value;
                            el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            console.log(`✅ Filled ${{name}}: ${{value}}`);
                            return true;
                        }}
                        console.log(`⚠️ Not found: ${{name}}`);
                        return false;
                    }}
                    
                    function selectDropdown(name, value) {{
                        let el = document.querySelector(`select[name="${{name}}"]`);
                        if (el) {{
                            for (let opt of el.options) {{
                                if (opt.textContent.trim() === value || opt.value === value) {{
                                    el.value = opt.value;
                                    el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                                    el.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                    console.log(`✅ Selected ${{name}}: ${{value}}`);
                                    return true;
                                }}
                            }}
                            el.value = value;
                            el.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            console.log(`✅ Selected ${{name}} by value: ${{value}}`);
                            return true;
                        }}
                        console.log(`⚠️ Dropdown not found: ${{name}}`);
                        return false;
                    }}
                    
                    // ========================================
                    // 1. PRIMARY HANDLER (Required)
                    // ========================================
                    fillInput('firstname', '{first}');
                    fillInput('lastname', '{last}');
                    fillInput('age', '23');
                    fillInput('youremail', '{email}');
                    fillInput('email', '{email}');
                    fillInput('confirmemail', '{email}');
                    
                    // ========================================
                    // 2. LOCATION (Required)
                    // ========================================
                    fillInput('tel', '{phone}');
                    fillInput('phone', '{phone}');
                    fillInput('address', 'ertyuyf456');
                    fillInput('city', 'cghj');
                    fillInput('state', 'fghjgh');
                    fillInput('zip', '34567');
                    fillInput('zipcode', '34567');
                    
                    // ========================================
                    // 3. ORGANIZATION/FARM (Required)
                    // ========================================
                    fillInput('farm', '{org_name}');
                    fillInput('organization', '{org_name}');
                    
                    // ========================================
                    // 4. THERAPY WITH EQUINE - "YES"
                    // ========================================
                    selectDropdown('currently', 'Yes');
                    
                    // ========================================
                    // 5. VOLUNTEER HANDLERS - "YES"
                    // ========================================
                    selectDropdown('handlers8', 'Yes');
                    
                    // ========================================
                    // 6. EQUINE OWNERSHIP - "YES"
                    // ========================================
                    selectDropdown('owned', 'Yes');
                    
                    // ========================================
                    // 7. EXPLANATION (Required Textarea - only if No selected)
                    // ========================================
                    // Since we selected "Yes" for owned, explanation might not be needed
                    // But still filling it just in case
                    fillInput('explain', 'All equines are owned by the primary handler');
                    
                    // ========================================
                    // 8. EQUINE #1 (Required Fields)
                    // ========================================
                    selectDropdown('type1', 'Miniature Horse');
                    fillInput('horseage1', '2');
                    fillInput('name1', '{eq1_name}');
                    
                    // ========================================
                    // 9. MORE THAN 6 EQUINES - "YES"
                    // ========================================
                    selectDropdown('equines7', 'Yes');
                    
                    console.log("=== ALL REQUIRED FIELDS FILLED ===");
                    return true;
                }})();
            """
            
            page.evaluate(js_code)
            logger.info("✅ All fields filled!")
            time.sleep(2)
            
            # ============================================================
            # UPLOAD PDF
            # ============================================================
            logger.info("📁 Uploading PDF...")
            try:
                file_input = page.locator('input[type="file"]').first
                file_input.set_input_files(pdf_path)
                time.sleep(2)
                logger.info("✅ PDF uploaded!")
            except Exception as e:
                logger.error(f"❌ Upload failed: {e}")
            
            # ============================================================
            # SOLVE CAPTCHA
            # ============================================================
            logger.info("🔐 Solving reCAPTCHA...")
            solver = TwoCaptcha(CAPTCHA_API_KEY)
            try:
                result = solver.recaptcha(sitekey=REAL_SITEKEY, url=TARGET_URL)
                captcha_token = result.get('code')
                if captcha_token:
                    logger.info("✅ reCAPTCHA solved!")
                    page.evaluate(f"""
                        (token) => {{
                            let textarea = document.querySelector('textarea[name="g-recaptcha-response"]');
                            if (textarea) {{
                                textarea.value = token;
                                textarea.dispatchEvent(new Event('input', {{ bubbles: true }}));
                                textarea.dispatchEvent(new Event('change', {{ bubbles: true }}));
                            }}
                            let div = document.getElementById('g-recaptcha-response');
                            if (div) {{
                                div.value = token;
                            }}
                        }}
                    """, captcha_token)
                    time.sleep(2)
            except Exception as e:
                logger.error(f"❌ Captcha failed: {e}")
            
            # ============================================================
            # SCREENSHOT BEFORE SUBMIT
            # ============================================================
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(SCREENSHOT_FOLDER, f"before_submit_{timestamp}.png")
            page.screenshot(path=screenshot_path)
            logger.info(f"📸 Screenshot saved: before_submit_{timestamp}.png")
            
            # ============================================================
            # CHECK VALIDATION ERRORS BEFORE SUBMIT
            # ============================================================
            logger.info("🔍 Checking for validation errors before submit...")
            errors_before = page.evaluate("""
                () => {
                    let errors = [];
                    document.querySelectorAll('.wpcf7-not-valid-tip, .wpcf7-validation-errors, .wpcf7-spam-blocked, .wpcf7-not-valid').forEach(el => {
                        if (el.innerText && el.innerText.trim()) {
                            errors.push(el.innerText.trim());
                        }
                    });
                    return errors;
                }
            """)
            
            if errors_before:
                logger.warning(f"⚠️ Validation errors before submit: {errors_before}")
            else:
                logger.info("✅ No validation errors found before submit")
            
            # ============================================================
            # MULTIPLE SUBMIT CLICKS
            # ============================================================
            logger.info("🚀 Submitting form (clicking multiple times)...")
            
            submit_btn = page.locator('input[type="submit"], button:has-text("SEND")').first
            submission_status = None
            
            for i in range(5):
                logger.info(f"🔄 Submit click #{i+1}")
                submit_btn.click()
                time.sleep(3)
                
                current_url = page.url
                logger.info(f"📍 Current URL: {current_url}")
                
                if "payment" in current_url.lower() or "checkout" in current_url.lower():
                    submission_status = 'mail_sent'
                    logger.info("🎉 Redirect to payment detected!")
                    break
                elif "thank" in current_url.lower() or "success" in current_url.lower():
                    submission_status = 'mail_sent'
                    logger.info("🎉 Thank you page detected!")
                    break
                else:
                    errors_after = page.evaluate("""
                        () => {
                            let errors = [];
                            document.querySelectorAll('.wpcf7-not-valid-tip, .wpcf7-validation-errors, .wpcf7-spam-blocked, .wpcf7-not-valid, .wpcf7-response-output').forEach(el => {
                                if (el.innerText && el.innerText.trim()) {
                                    errors.push(el.innerText.trim());
                                }
                            });
                            return errors;
                        }
                    """)
                    
                    if errors_after:
                        logger.warning(f"⚠️ Errors after submit #{i+1}: {errors_after}")
                        
                        invalid_fields = page.evaluate("""
                            () => {
                                let fields = [];
                                document.querySelectorAll('.wpcf7-not-valid').forEach(el => {
                                    let name = el.getAttribute('name') || el.id || 'unknown';
                                    fields.push(name);
                                });
                                return fields;
                            }
                        """)
                        if invalid_fields:
                            logger.warning(f"⚠️ Invalid fields: {invalid_fields}")
                    else:
                        logger.info(f"⏳ No errors, trying again...")
            
            # ============================================================
            # EXTRA WAIT FOR REDIRECT
            # ============================================================
            if submission_status != 'mail_sent':
                logger.info("⏳ Waiting longer for redirect...")
                for _ in range(30):
                    time.sleep(1)
                    if "payment" in page.url.lower() or "checkout" in page.url.lower():
                        submission_status = 'mail_sent'
                        logger.info("🎉 Redirect detected!")
                        break
                    elif "thank" in page.url.lower() or "success" in page.url.lower():
                        submission_status = 'mail_sent'
                        logger.info("🎉 Thank you page detected!")
                        break
            
            # ============================================================
            # FINAL STATUS
            # ============================================================
            if submission_status == 'mail_sent':
                logger.info("🎉 SUCCESS! Form submitted successfully!")
            else:
                logger.warning("⚠️ Form may not have submitted. Check manually.")
                error_screenshot = os.path.join(SCREENSHOT_FOLDER, f"error_state_{timestamp}.png")
                page.screenshot(path=error_screenshot)
                logger.info(f"📸 Error state screenshot: {error_screenshot}")
            
            final_screenshot = os.path.join(SCREENSHOT_FOLDER, f"final_{timestamp}.png")
            page.screenshot(path=final_screenshot)
            
            context.close()
            return {'submission_status': submission_status, 'email': email}, "success"
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            if context:
                try: context.close()
                except: pass
            return None, "error"


def run_bot():
    print("\n" + "="*70)
    print("🤖 AMTHA FORM - ALL DROPDOWNS = YES")
    print("="*70 + "\n")
    
    pdf_path = get_pdf_path()
    if not pdf_path:
        logger.error(f"❌ PDF not found: {PDF_FILE_NAME}")
        return
    
    logger.info(f"✅ PDF: {pdf_path}")
    
    success_count = 0
    max_success = 1
    
    for attempt in range(1, 6):
        if success_count >= max_success:
            print("\n🎉 TARGET REACHED!\n")
            break
        
        print(f"\n🔄 Attempt #{attempt}")
        
        first, last, email, phone, org_name, eq1_name = generate_random_data()
        print(f"📧 Email: {email}")
        print(f"📝 Equine 1: {eq1_name}")
        
        result, status = submit_form(
            pdf_path, first, last, email, phone, org_name, eq1_name
        )
        
        if status == "success" and result and result.get('submission_status') == 'mail_sent':
            success_count += 1
            print(f"\n🎉 SUCCESS! Email: {email}\n")
            break
        else:
            logger.warning(f"⚠️ Attempt {attempt} failed")
        
        time.sleep(random.uniform(5, 10))
    
    if success_count == 0:
        print("\n❌ All attempts failed!")
    else:
        print(f"\n✅ Submitted {success_count} form(s)!")


if __name__ == "__main__":
    run_bot()