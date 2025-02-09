import requests
import textwrap
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🔹 Bot Configuration (Only Bot Token Required)
BOT_TOKEN = "7289532935:AAE_pNosgh7e86RwL81mJYjGkeLiV-m0ao4"  # Replace with your Bot Token
OWNER_ID = 7222795580  # Replace with your Telegram user ID (Owner Only)

# Database to track stats
stats = {"total_users": set(), "sites_checked": 0}

# Initialize Pyrogram Bot (No API_ID/API_HASH Required)
app = Client("PaymentGatewayBot", bot_token=BOT_TOKEN)


def format_message(content):
    """Auto-wraps text for better mobile display."""
    return textwrap.fill(content, width=40)


def find_captcha(response_text):
    """Detects the type of captcha used on the website."""
    response_text_lower = response_text.lower()
    if 'recaptcha' in response_text_lower:
        return '🟢 Google reCAPTCHA ✅'
    elif 'hcaptcha' in response_text_lower:
        return '🟡 hCaptcha ✅'
    return '🔴 No Captcha Detected 🚫'


def detect_cloudflare(response):
    """Detects if Cloudflare protection is enabled on the website."""
    cloudflare_indicators = ["cloudflare.com", "__cfduid", "cf-ray", "cf-cache-status", "server"]
    response_text_lower = response.text.lower()
    return any(indicator in response_text_lower or indicator in response.headers for indicator in cloudflare_indicators)


def find_payment_gateways(response_text):
    """Detects all known payment gateways in a website's source code."""
    lower_text = response_text.lower()
    gateways = {
        "paypal": "💰 PayPal", "stripe": "💳 Stripe", "braintree": "🏦 Braintree",
        "square": "🟦 Square", "authorize.net": "🛡️ Authorize.Net", "2checkout": "💵 2Checkout",
        "adyen": "💸 Adyen", "worldpay": "🌍 Worldpay", "skrill": "💲 Skrill",
        "neteller": "🟢 Neteller", "payoneer": "🟡 Payoneer", "klarna": "🛒 Klarna",
        "alipay": "🇨🇳 Alipay", "wechat pay": "🇨🇳 WeChat Pay", "razorpay": "🇮🇳 Razorpay",
        "instamojo": "💰 Instamojo", "ccavenue": "🏦 CCAvenue", "payu": "🟠 PayU",
        "mobikwik": "📱 MobiKwik", "cashfree": "💵 Cashfree", "flutterwave": "🌊 Flutterwave",
    }
    detected_gateways = [value for key, value in gateways.items() if key in lower_text]
    return detected_gateways if detected_gateways else ["❓ Unknown"]


def fetch_website_data(url):
    """Fetches website content and analyzes security & payment methods."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return {
            "detected_gateways": find_payment_gateways(response.text),
            "detected_captcha": find_captcha(response.text),
            "cloudflare_protected": detect_cloudflare(response),
        }
    except requests.RequestException:
        return None


@app.on_message(filters.command("gate"))
async def check_payment_gateways(client, message):
    """Handles /gate command and fetches payment gateway details."""
    user_id = message.from_user.id
    stats["total_users"].add(user_id)  # Track unique users

    processing_message = await message.reply("🔍 **Scanning the website... Please wait...**", disable_web_page_preview=True)

    website_url = message.text[len('/gate'):].strip()
    if not website_url.startswith(("http://", "https://")):
        website_url = "http://" + website_url  

    data = fetch_website_data(website_url)

    if not data:
        await processing_message.edit_text("⚠️ **Error: Could not retrieve details. Ensure the website is reachable.**")
        return

    stats["sites_checked"] += 1  # Increment site count

    gateways = ', '.join(data['detected_gateways'])
    captcha = data['detected_captcha']
    cloudflare = "✅ Enabled" if data['cloudflare_protected'] else "🚫 Not Enabled"

    # **Auto-wrap text for better display**
    site_text = format_message(f"🌐 Site: {website_url}")
    gateways_text = format_message(f"💳 Payment Gateways: {gateways}")
    captcha_text = format_message(f"🔒 Captcha: {captcha}")
    cloudflare_text = format_message(f"☁️ Cloudflare: {cloudflare}")

    result_message = (
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ {site_text}\n"
        f"│ {gateways_text}\n"
        f"│ {captcha_text}\n"
        f"│ {cloudflare_text}\n"
        "╰━━━━━━━━━━━━━━━━━━━╯"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📢 Join @PhiloBots", url="https://t.me/PhiloBots")]]
    )

    await processing_message.edit_text(result_message, disable_web_page_preview=True, reply_markup=keyboard)


if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run()
