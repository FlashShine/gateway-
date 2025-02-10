import requests
import textwrap
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# 🌟 Bot Configuration
API_ID = 22318470  # 🔥 Replace with your API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # 🔥 Replace with your API Hash
BOT_TOKEN = "7289532935:AAFg3xuwRW--6t8Eqo7GU-qTbrIRJG8nhM8"  # 🔥 Replace with your Bot Token
OWNER_ID = 7222795580  # 🔥 Replace with your Telegram user ID

# 🚀 Initialize Pyrogram Bot
app = Client("PaymentGatewayBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# 📊 Database to track stats
stats = {"total_users": set(), "sites_checked": 0}


def format_message(content):
    """✨ Auto-wraps text to fit mobile screens."""
    return textwrap.fill(content, width=40)


def find_payment_gateways(response_text):
    """💰 Scans the response text for known payment gateways."""
    lower_text = response_text.lower()
    gateways = {
        "paypal": "💰 PayPal", "stripe": "💳 Stripe", "braintree": "🏦 Braintree",
        "square": "🟦 Square", "authorize.net": "🛡️ Authorize.Net", "razorpay": "🇮🇳 Razorpay"
    }
    detected_gateways = [value for key, value in gateways.items() if key in lower_text]
    return detected_gateways if detected_gateways else ["❓ Unknown"]


def find_captcha(response_text):
    """🛡️ Detects the type of captcha used on the website."""
    response_text_lower = response_text.lower()
    if 'recaptcha' in response_text_lower:
        return '🟢 Google reCAPTCHA ✅'
    elif 'hcaptcha' in response_text_lower:
        return '🟡 hCaptcha ✅'
    return '🔴 No Captcha Detected ❌'


def detect_cloudflare(response):
    """☁️ Detects if Cloudflare protection is enabled on the website."""
    cloudflare_indicators = ["cloudflare.com", "__cfduid", "cf-ray", "cf-cache-status", "server"]
    response_text_lower = response.text.lower()
    return any(indicator in response_text_lower or indicator in response.headers for indicator in cloudflare_indicators)


def detect_payment_type(response_text):
    """🔒 Detects if the Payment Gateway is 2D or 3D Secure."""
    response_text_lower = response_text.lower()
    if "3d secure" in response_text_lower or "stripe3dsecure" in response_text_lower:
        return "🔐 3D Secure ✅"
    elif "stripe-checkout" in response_text_lower or "2d secure" in response_text_lower:
        return "🔓 2D Payment ❌"
    return "⚠️ Unknown Payment Type"


def fetch_website_data(url):
    """🌐 Fetches website content and analyzes security & payment methods."""
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return {
            "detected_gateways": find_payment_gateways(response.text),
            "detected_captcha": find_captcha(response.text),
            "cloudflare_protected": detect_cloudflare(response),
            "payment_type": detect_payment_type(response.text),
        }
    except requests.RequestException:
        return None


@app.on_message(filters.command("start"))
async def start(client, message):
    """👋 Handles /start command."""
    user = message.from_user
    start_msg = (
        f"👋 **Welcome {user.first_name}!**\n\n"
        "🚀 **This bot helps you check payment gateways, captchas, payment security, and Cloudflare protection** on any website.\n\n"
        "📌 **Simply send a website URL and the bot will analyze it!**\n\n"
        "🔗 **Join [@PhiloBots](https://t.me/PhiloBots) for More Tools!**"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join @PhiloBots", url="https://t.me/PhiloBots")]])
    await message.reply(start_msg, reply_markup=keyboard)


@app.on_message(filters.text & ~filters.command(["start", "profile", "stats"]))
async def auto_check_site(client, message):
    """🔍 Automatically checks URLs sent without needing a command."""
    user_id = message.from_user.id
    user_name = message.from_user.first_name
    stats["total_users"].add(user_id)  # Track unique users

    # Extract URL from message
    urls = re.findall(r'https?://\S+', message.text)
    if not urls:
        return

    website_url = urls[0]

    processing_message = await message.reply("🔍 **Scanning the website... Please wait...**", disable_web_page_preview=True)

    data = fetch_website_data(website_url)

    if not data:
        await processing_message.edit_text("⚠️ **Error: Could not retrieve details. Ensure the website is reachable.**")
        return

    stats["sites_checked"] += 1  # Increment site count

    gateways = ', '.join(data['detected_gateways'])
    captcha = data['detected_captcha']
    cloudflare = "✅ Enabled" if data['cloudflare_protected'] else "🚫 Not Enabled"
    payment_type = data["payment_type"]

    # 📝 Auto-wrap text for better display
    site_text = format_message(f"🌐 **Site:** {website_url}")
    gateways_text = format_message(f"💳 **Payment Gateways:** {gateways}")
    captcha_text = format_message(f"🔒 **Captcha:** {captcha}")
    cloudflare_text = format_message(f"☁️ **Cloudflare:** {cloudflare}")
    payment_text = format_message(f"💠 **Payment Type:** {payment_type}")
    checked_by_text = format_message(f"👤 **Checked By:** {user_name}")

    result_message = (
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ {site_text}\n"
        f"│ {gateways_text}\n"
        f"│ {captcha_text}\n"
        f"│ {cloudflare_text}\n"
        f"│ {payment_text}\n"
        f"│ {checked_by_text}\n"
        "╰━━━━━━━━━━━━━━━━━━━╯"
    )

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📢 Join @PhiloBots", url="https://t.me/PhiloBots")]]
    )

    await processing_message.edit_text(result_message, disable_web_page_preview=True, reply_markup=keyboard)


if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run()
