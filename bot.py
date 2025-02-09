import requests
import asyncio
from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Configuration
API_ID = 22318470  # Replace with your API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # Replace with your API Hash
BOT_TOKEN = "7289532935:AAGPfxR6S9z0Ri-6JMXs5StlqQg9x-a2dps"  # Replace with your Bot Token
OWNER_ID = 7222795580  # Replace with your Telegram user ID

# Database to track stats
stats = {"total_users": set(), "sites_checked": 0}

# Initialize Pyrogram Bot
app = Client("PaymentGatewayBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


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
    """Scans the response text for known payment gateways."""
    lower_text = response_text.lower()
    gateways = {
        "paypal": "💰 PayPal", "stripe": "💳 Stripe", "braintree": "🏦 Braintree", 
        "square": "🟦 Square", "authorize.net": "🛡️ Authorize.Net", "2checkout": "💵 2Checkout",
        "adyen": "💸 Adyen", "worldpay": "🌍 Worldpay", "skrill": "💲 Skrill", 
        "neteller": "🟢 Neteller", "payoneer": "🟡 Payoneer", "klarna": "🛒 Klarna", 
        "alipay": "🇨🇳 Alipay", "wechat pay": "🇨🇳 WeChat Pay", "razorpay": "🇮🇳 Razorpay",
        "instamojo": "🇮🇳 Instamojo", "ccavenue": "🏦 CCAvenue", "payu": "🟠 PayU",
        "mobikwik": "📱 MobiKwik", "cashfree": "💳 Cashfree", "flutterwave": "🌊 Flutterwave",
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
    except requests.RequestException as e:
        print(f"[ERROR] Request failed: {e}")
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

    result_message = (
        "📌 **Gateway Result**\n"
        "╭───────────────────────────╮\n"
        f"│ 🌐 **Site:** `{website_url}`\n"
        f"│ 💳 **Payment Gateways:** `{gateways}`\n"
        f"│ 🔒 **Captcha:** `{captcha}`\n"
        f"│ ☁️ **Cloudflare:** `{cloudflare}`\n"
        "╰───────────────────────────╯\n\n"
        "🔗 [Join @PhiloBots for More Tools](https://t.me/PhiloBots)"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📢 Join @PhiloBots", url="https://t.me/PhiloBots")]]
    )

    await processing_message.edit_text(result_message, disable_web_page_preview=True, reply_markup=keyboard)


if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run()
