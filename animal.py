import os
import time
import random
import string
import logging
from datetime import datetime
from dotenv import load_dotenv
from twocaptcha import TwoCaptcha
from faker import Faker

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

# Initialize Faker
fake = Faker()


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
    # Faker se real data generate karo
    first = fake.first_name()
    last = fake.last_name()
    email = fake.email()
    phone = fake.phone_number()[:10]  # 10 digit phone
    org_name = fake.company()[:20]
    
    eq1_name = fake.word() + "_" + ''.join(random.choices(string.ascii_lowercase, k=3))
    
    eq_names = {}
    for i in range(2, 7):
        eq_names[f'eq{i}_name'] = fake.word() + "_" + ''.join(random.choices(string.ascii_lowercase, k=4))
    
    return first, last, email, phone, org_name, eq1_name, eq_names


def submit_form(pdf_path, first, last, email, phone, org_name, eq1_name, eq_names):
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
            
            logger.info("📝 Filling all fields...")
            
            equine_js = ""
            for i in range(2, 7):
                eq_name = eq_names[f'eq{i}_name']
                equine_js += f"""
                    let type{i} = document.querySelector(`select[name="type{i}"]`);
                    if (type{i}) {{
                        let opts = type{i}.querySelectorAll('option');
                        for (let opt of opts) {{
                            if (opt.textContent.trim() === 'Miniature Horse') {{
                                type{i}.value = opt.value;
                                type{i}.dispatchEvent(new Event('change', {{bubbles: true}}));
                                break;
                            }}
                        }}
                    }}
                    let age{i} = document.querySelector(`input[name="horseage{i}"]`);
                    if (age{i}) {{
                        age{i}.value = '{i + 1}';
                        age{i}.dispatchEvent(new Event('input', {{bubbles: true}}));
                        age{i}.dispatchEvent(new Event('change', {{bubbles: true}}));
                    }}
                    let name{i} = document.querySelector(`input[name="name{i}"]`);
                    if (name{i}) {{
                        name{i}.value = '{eq_name}';
                        name{i}.dispatchEvent(new Event('input', {{bubbles: true}}));
                        name{i}.dispatchEvent(new Event('change', {{bubbles: true}}));
                    }}
                """
            
            js_code = f"""
                (function() {{
                    console.log("=== FILLING ALL FIELDS ===");
                    
                    function fillField(el, value) {{
                        if (!el) return;
                        el.value = value;
                        el.dispatchEvent(new Event('input', {{bubbles: true}}));
                        el.dispatchEvent(new Event('change', {{bubbles: true}}));
                        el.dispatchEvent(new Event('blur', {{bubbles: true}}));
                        console.log(`✅ ${{el.name}} = ${{value}}`);
                    }}
                    
                    function selectDropdown(el, value) {{
                        if (!el) return;
                        let opts = el.querySelectorAll('option');
                        for (let opt of opts) {{
                            if (opt.textContent.trim() === value || opt.value === value) {{
                                el.value = opt.value;
                                el.dispatchEvent(new Event('change', {{bubbles: true}}));
                                console.log(`✅ ${{el.name}} = ${{value}}`);
                                return;
                            }}
                        }}
                        if (el.options.length > 1) {{
                            el.value = el.options[1].value;
                            el.dispatchEvent(new Event('change', {{bubbles: true}}));
                        }}
                    }}
                    
                    // ========================================
                    // 1. PRIMARY HANDLER
                    // ========================================
                    fillField(document.querySelector('input[name="firstname"]'), '{first}');
                    fillField(document.querySelector('input[name="lastname"]'), '{last}');
                    fillField(document.querySelector('input[name="age"]'), '23');
                    fillField(document.querySelector('input[name="youremail"]'), '{email}');
                    fillField(document.querySelector('input[name="confirmemail"]'), '{email}');
                    
                    // ========================================
                    // 2. PHONE
                    // ========================================
                    let phoneNames = ['tel', 'phone', 'phonenumber', 'mobile'];
                    phoneNames.forEach(name => {{
                        let el = document.querySelector(`input[name="${{name}}"]`);
                        if (el) {{
                            el.value = '{phone}';
                            el.dispatchEvent(new Event('input', {{bubbles: true}}));
                            el.dispatchEvent(new Event('change', {{bubbles: true}}));
                            el.dispatchEvent(new Event('blur', {{bubbles: true}}));
                            console.log(`✅ phone (${{name}}) = {phone}`);
                        }}
                    }});
                    
                    // ========================================
                    // 3. ADDRESS
                    // ========================================
                    fillField(document.querySelector('input[name="address"]'), '123 Main Street');
                    fillField(document.querySelector('input[name="city"]'), 'New York');
                    fillField(document.querySelector('input[name="state"]'), 'NY');
                    
                    // ========================================
                    // 4. ZIP
                    // ========================================
                    let zipNames = ['zip', 'zipcode', 'postal', 'postalcode'];
                    let zipFilled = false;
                    zipNames.forEach(name => {{
                        let el = document.querySelector(`input[name="${{name}}"]`);
                        if (el && !zipFilled) {{
                            el.value = '10001';
                            el.dispatchEvent(new Event('input', {{bubbles: true}}));
                            el.dispatchEvent(new Event('change', {{bubbles: true}}));
                            el.dispatchEvent(new Event('blur', {{bubbles: true}}));
                            console.log(`✅ zip (${{name}}) = 10001`);
                            zipFilled = true;
                        }}
                    }});
                    
                    // ========================================
                    // 5. ORGANIZATION/FARM
                    // ========================================
                    fillField(document.querySelector('input[name="farm"]'), '{org_name}');
                    
                    // ========================================
                    // 6. DROPDOWNS - "Yes"
                    // ========================================
                    selectDropdown(document.querySelector('select[name="currently"]'), 'Yes');
                    selectDropdown(document.querySelector('select[name="handlers8"]'), 'Yes');
                    selectDropdown(document.querySelector('select[name="owned"]'), 'Yes');
                    selectDropdown(document.querySelector('select[name="equines7"]'), 'Yes');
                    
                    // ========================================
                    // 7. EXPLANATION
                    // ========================================
                    fillField(document.querySelector('textarea[name="explain"]'), 'All equines are owned by the primary handler');
                    
                    // ========================================
                    // 8. EQUINE #1
                    // ========================================
                    selectDropdown(document.querySelector('select[name="type1"]'), 'Miniature Horse');
                    fillField(document.querySelector('input[name="horseage1"]'), '2');
                    fillField(document.querySelector('input[name="name1"]'), '{eq1_name}');
                    
                    // ========================================
                    // 9. EQUINE #2 TO #6
                    // ========================================
                    {equine_js}
                    
                    console.log("=== ALL FIELDS FILLED ===");
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
                result = solver.recaptcha(
                    sitekey=REAL_SITEKEY,
                    url=TARGET_URL,
                    version='v2',
                    invisible=1
                )
                captcha_token = result.get('code')
                if captcha_token:
                    logger.info("✅ reCAPTCHA solved!")
                    page.evaluate(f"""
                        (token) => {{
                            document.querySelectorAll('textarea[name="g-recaptcha-response"]').forEach(el => {{
                                el.value = token;
                                el.dispatchEvent(new Event('input', {{bubbles: true}}));
                                el.dispatchEvent(new Event('change', {{bubbles: true}}));
                            }});
                            let hidden = document.querySelector('input[name="_wpcf7_recaptcha_response"]');
                            if (hidden) {{
                                hidden.value = token;
                                hidden.dispatchEvent(new Event('input', {{bubbles: true}}));
                            }}
                            let recaptchaDiv = document.querySelector('.g-recaptcha');
                            if (recaptchaDiv && recaptchaDiv.dataset.callback) {{
                                let callback = recaptchaDiv.dataset.callback;
                                if (typeof window[callback] === 'function') {{
                                    window[callback](token);
                                }}
                            }}
                        }}
                    """, captcha_token)
                    time.sleep(3)
            except Exception as e:
                logger.error(f"❌ Captcha failed: {e}")
            
            # ============================================================
            # SCREENSHOT
            # ============================================================
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(SCREENSHOT_FOLDER, f"before_submit_{timestamp}.png")
            page.screenshot(path=screenshot_path)
            logger.info(f"📸 Screenshot saved")
            
            # ============================================================
            # SUBMIT - ONLY 1 ATTEMPT
            # ============================================================
            logger.info("🚀 Submitting form...")
            submit_btn = page.locator('input[type="submit"], button:has-text("SEND")').first
            submission_status = None
            
            for i in range(2):
                logger.info(f"🔄 Submit click #{i+1}")
                submit_btn.click()
                time.sleep(4)
                
                current_url = page.url
                if "payment" in current_url.lower() or "checkout" in current_url.lower():
                    submission_status = 'mail_sent'
                    logger.info("🎉 Redirect to payment detected!")
                    break
                elif "thank" in current_url.lower() or "success" in current_url.lower():
                    submission_status = 'mail_sent'
                    logger.info("🎉 Thank you page detected!")
                    break
            
            # ============================================================
            # SUCCESS OUTPUT
            # ============================================================
            if submission_status == 'mail_sent':
                print("\n" + "="*70)
                print("🎉🎉🎉 SUCCESS! FORM SUBMITTED! 🎉🎉🎉")
                print("="*70)
                print(f"📧 Email: {email}")
                print(f"🔑 Password: {fake.password(length=12)}")
                print(f"📄 PDF Uploaded: {os.path.basename(pdf_path)}")
                print(f"📁 PDF Path: {pdf_path}")
                print("="*70 + "\n")
                
                logger.info("🎉 SUCCESS!")
            else:
                logger.warning("⚠️ Form may not have submitted.")
                error_screenshot = os.path.join(SCREENSHOT_FOLDER, f"error_state_{timestamp}.png")
                page.screenshot(path=error_screenshot)
            
            final_screenshot = os.path.join(SCREENSHOT_FOLDER, f"final_{timestamp}.png")
            page.screenshot(path=final_screenshot)
            
            context.close()
            return {'submission_status': submission_status, 'email': email, 'password': fake.password(length=12)}, "success"
            
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            if context:
                try: context.close()
                except: pass
            return None, "error"


def run_bot():
    print("\n" + "="*70)
    print("🤖 AMTHA FORM - SINGLE ATTEMPT WITH FAKER")
    print("="*70 + "\n")
    
    pdf_path = get_pdf_path()
    if not pdf_path:
        logger.error(f"❌ PDF not found: {PDF_FILE_NAME}")
        return
    
    logger.info(f"✅ PDF: {pdf_path}")
    
    # ONLY 1 ATTEMPT - Loop removed
    print(f"\n🔄 Submitting form...")
    
    first, last, email, phone, org_name, eq1_name, eq_names = generate_random_data()
    
    print(f"📧 Email: {email}")
    print(f"👤 Name: {first} {last}")
    print(f"📱 Phone: {phone}")
    print(f"🏢 Organization: {org_name}")
    
    result, status = submit_form(
        pdf_path, first, last, email, phone, org_name, eq1_name, eq_names
    )
    
    if status == "success" and result and result.get('submission_status') == 'mail_sent':
        print("\n" + "="*70)
        print("🎉🎉🎉 FORM SUBMITTED SUCCESSFULLY! 🎉🎉🎉")
        print("="*70)
        print(f"📧 Email: {result.get('email')}")
        print(f"🔑 Password: {result.get('password', 'N/A')}")
        print(f"📄 PDF: {os.path.basename(pdf_path)}")
        print(f"📁 PDF Path: {pdf_path}")
        print("="*70 + "\n")
    else:
        print("\n❌ Form submission failed!")
        print("Please check manually.")


if __name__ == "__main__":
    run_bot()