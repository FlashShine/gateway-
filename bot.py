import requests
import textwrap
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Configuration (Only BOT TOKEN Required)
BOT_TOKEN = "7289532935:AAE_pNosgh7e86RwL81mJYjGkeLiV-m0ao4"  # Replace with your bot token
OWNER_ID = 7222795580  # Replace with your Telegram user ID

# Database to track stats
stats = {"total_users": set(), "sites_checked": 0}

# Initialize Pyrogram Bot (No API ID & API HASH Required)
app = Client("PaymentGatewayBot", bot_token=BOT_TOKEN)


def format_message(content):
    """Auto-wraps text to fit mobile screens."""
    return textwrap.fill(content, width=40)


def find_payment_gateways(response_text):
    """Scans the response text for known payment gateways."""
    lower_text = response_text.lower()
    gateways = {
        "paypal": "💰 PayPal", "stripe": "💳 Stripe", "braintree": "🏦 Braintree",
        "square": "🟦 Square", "authorize.net": "🛡️ Authorize.Net", "razorpay": "🇮🇳 Razorpay"
    }
    detected_gateways = [value for key, value in gateways.items() if key in lower_text]
    return detected_gateways if detected_gateways else ["❓ Unknown"]


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


@app.on_message(filters.command("start"))
async def start(client, message):
    """Handles /start command."""
    user = message.from_user
    start_msg = (
        f"👋 **Welcome {user.first_name}!**\n\n"
        "🚀 This bot helps you **check payment gateways, captchas, and Cloudflare protection** on any website.\n\n"
        "**📌 Available Commands:**\n"
        "🔹 `/gate <site>` - Check payment gateways\n"
        "🔹 `/profile` - View your info\n"
        "🔹 `/stats` - Bot statistics (Owner only)\n\n"
        "🔗 **Join [@PhiloBots](https://t.me/PhiloBots) for More Tools**"
    )
    keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("📢 Join @PhiloBots", url="https://t.me/PhiloBots")]])
    await message.reply(start_msg, reply_markup=keyboard)


@app.on_message(filters.command("profile"))
async def profile(client, message):
    """Handles /profile command to show user information."""
    user = message.from_user
    profile_msg = (
        f"👤 **User Profile**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"🆔 **User ID:** `{user.id}`\n"
        f"👤 **Name:** `{user.first_name} {user.last_name or ''}`\n"
        f"🔹 **Username:** `@{user.username or 'N/A'}`\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(profile_msg)


@app.on_message(filters.command("stats") & filters.user(OWNER_ID))
async def stats_command(client, message):
    """Handles /stats command for bot statistics (Owner only)."""
    total_users = len(stats["total_users"])
    sites_checked = stats["sites_checked"]
    stats_msg = (
        f"📊 **Bot Statistics**\n"
        f"━━━━━━━━━━━━━━━━━━━\n"
        f"👥 **Total Users:** `{total_users}`\n"
        f"🌐 **Sites Checked:** `{sites_checked}`\n"
        f"━━━━━━━━━━━━━━━━━━━"
    )
    await message.reply(stats_msg)


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
    site_text = format_message(f"🌐 **Site:** {website_url}")
    gateways_text = format_message(f"💳 **Payment Gateways:** {gateways}")
    captcha_text = format_message(f"🔒 **Captcha:** {captcha}")
    cloudflare_text = format_message(f"☁️ **Cloudflare:** {cloudflare}")

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
