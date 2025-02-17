import requests
import textwrap
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ☫ Bot Configuration
API_ID = 22318470  # ☫ Replace with your API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # ☫ Replace with your API Hash
BOT_TOKEN = "7289532935:AAFg3xuwRW--6t8Eqo7GU-qTbrIRJG8nhM8"  # ☫ Replace with your Bot Token
OWNER_ID = 7222795580  # ☫ Replace with your Telegram user ID

# ☫ Initialize Pyrogram Bot
app = Client("PaymentGatewayBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ☫ Database to track stats and registrations
stats = {"total_users": set(), "sites_checked": 0}
registered_users = set()

def format_message(content):
    """☫ Auto-wraps text to fit mobile screens."""
    return textwrap.fill(content, width=40)


def fetch_website_data(url):
    """☫ Fetches website content and analyzes security & payment methods."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None


def detect_payment_gateways(response_text):
    """☫ Detects all known payment gateways in website source."""
    gateways = {
        "paypal": "PayPal",
        "stripe": "Stripe",
        "braintree": "Braintree",
        "square": "Square",
        "authorize.net": "Authorize.Net",
        "razorpay": "Razorpay",
        "adyen": "Adyen",
        "payu": "PayU",
        "worldpay": "WorldPay",
        "skrill": "Skrill",
        "payoneer": "Payoneer",
        "paytm": "Paytm",
        "wepay": "WePay",
        "klarna": "Klarna",
        "afterpay": "Afterpay",
        "alipay": "Alipay",
        "unionpay": "UnionPay",
        "amazonpay": "Amazon Pay",
        "applepay": "Apple Pay",
        "googlepay": "Google Pay",
    }
    found_gateways = [name for key, name in gateways.items() if key in response_text.lower()]
    return found_gateways if found_gateways else ["No Payment Gateways Detected"]


def detect_captcha(response_text):
    """☫ Detects captcha protection on the website."""
    if "recaptcha" in response_text.lower():
        return "Google reCAPTCHA"
    elif "hcaptcha" in response_text.lower():
        return "hCaptcha"
    return "No Captcha Detected"


def detect_cloudflare(response_text):
    """☫ Detects Cloudflare protection on the website."""
    cloudflare_indicators = ["cloudflare.com", "__cfduid", "cf-ray", "cf-cache-status"]
    return any(indicator in response_text.lower() for indicator in cloudflare_indicators)


def detect_payment_type(response_text):
    """☫ Detects if the Payment Gateway is 2D or 3D Secure."""
    if "3d secure" in response_text.lower() or "stripe3dsecure" in response_text.lower():
        return "3D Secure Payment"
    elif "stripe-checkout" in response_text.lower() or "2d secure" in response_text.lower():
        return "2D Payment"
    return "Unknown Payment Type"


@app.on_message(filters.text & ~filters.command(["start", "profile", "stats", "register"]))
async def auto_check_site(client, message):
    """☫ Automatically checks URLs sent without needing a command."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    if user_id not in registered_users:
        await message.reply("☫ Please register with /register before using the bot.")
        return

    stats["total_users"].add(user_id)  # Track unique users
    urls = re.findall(r'https?://\S+', message.text)
    if not urls:
        return

    website_url = urls[0]
    processing_message = await message.reply("☫ Scanning... Please wait...", disable_web_page_preview=True)
    response_text = fetch_website_data(website_url)

    if not response_text:
        await processing_message.edit_text("☫ Error: Could not retrieve details. Ensure the website is reachable.")
        return

    stats["sites_checked"] += 1  # Increment site count
    detected_gateways = detect_payment_gateways(response_text)
    detected_captcha = detect_captcha(response_text)
    cloudflare_status = "Enabled" if detect_cloudflare(response_text) else "Not Enabled"
    payment_type = detect_payment_type(response_text)

    site_text = format_message(f"☫ Site: {website_url}")
    gateway_text = format_message(f"☫ Payment Gateways: {', '.join(detected_gateways)}")
    captcha_text = format_message(f"☫ Captcha: {detected_captcha}")
    cloudflare_text = format_message(f"☫ Cloudflare Protection: {cloudflare_status}")
    payment_text = format_message(f"☫ Payment Type: {payment_type}")
    checked_by_text = format_message(f"☫ Checked By: {user_name}")

    result_message = (
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ {site_text}\n"
        f"│ {gateway_text}\n"
        f"│ {captcha_text}\n"
        f"│ {cloudflare_text}\n"
        f"│ {payment_text}\n"
        f"│ {checked_by_text}\n"
        "╰━━━━━━━━━━━━━━━━━━━╯"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("☫ Recheck", callback_data=f"recheck_{website_url}")],
        [InlineKeyboardButton("☫ Join @PhiloBots", url="https://t.me/PhiloBots")]
    ])
    await processing_message.edit_text(result_message, disable_web_page_preview=True, reply_markup=keyboard)

if __name__ == "__main__":
    print("☫ Bot is running...")
    app.run()
