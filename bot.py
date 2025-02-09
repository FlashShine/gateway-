import requests
import asyncio
from pyrogram import Client, filters, types
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Bot Configuration
API_ID = 22318470  # Replace with your API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # Replace with your API Hash
BOT_TOKEN = "7289532935:AAGWWNDhvUkDjVdSL5VE2N0uzzKEXTnwVcU"  # Replace with your Bot Token
OWNER_ID = 7222795580  # Replace with your Telegram user ID

# Database to track stats
stats = {"total_users": set(), "sites_checked": 0}

# Initialize Pyrogram Bot
app = Client("PaymentGatewayBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)


def format_message(content):
    """Auto-adjust message width for user's mobile screen."""
    max_width = 30  # Default width
    lines = content.split("\n")
    formatted_lines = [f"│ {line.ljust(max_width)} │" for line in lines]
    return "\n".join(formatted_lines)


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
        "🔗 **Join [@PhiloBots](https://t.me/PhiloBots) for more tools**"
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


def find_captcha(response_text):
    """Detects the type of captcha used on the website."""
    response_text_lower = response_text.lower()
    if 'recaptcha' in response_text_lower:
        return '🟢 𝗚𝗼𝗼𝗴𝗹𝗲 𝗿𝗲𝗖𝗔𝗣𝗧𝗖𝗛𝗔 ✅'
    elif 'hcaptcha' in response_text_lower:
        return '🟡 𝗵𝗖𝗮𝗽𝘁𝗰𝗵𝗮 ✅'
    return '🔴 𝗡𝗼 𝗖𝗮𝗽𝘁𝗰𝗵𝗮 𝗗𝗲𝘁𝗲𝗰𝘁𝗲𝗱 🚫'


def detect_cloudflare(response):
    """Detects if Cloudflare protection is enabled on the website."""
    cloudflare_indicators = ["cloudflare.com", "__cfduid", "cf-ray", "cf-cache-status", "server"]
    response_text_lower = response.text.lower()
    return any(indicator in response_text_lower or indicator in response.headers for indicator in cloudflare_indicators)


def find_payment_gateways(response_text):
    """Scans the response text for known payment gateways."""
    lower_text = response_text.lower()
    gateways = {
        "paypal": "💰 𝗣𝗮𝘆𝗣𝗮𝗹", "stripe": "💳 𝗦𝘁𝗿𝗶𝗽𝗲", "braintree": "🏦 𝗕𝗿𝗮𝗶𝗻𝘁𝗿𝗲𝗲", 
        "square": "🟦 𝗦𝗾𝘂𝗮𝗿𝗲", "authorize.net": "🛡️ 𝗔𝘂𝘁𝗵𝗼𝗿𝗶𝘇𝗲.𝗡𝗲𝘁", "razorpay": "🇮🇳 𝗥𝗮𝘇𝗼𝗿𝗣𝗮𝘆"
    }
    detected_gateways = [value for key, value in gateways.items() if key in lower_text]
    return detected_gateways if detected_gateways else ["❓ 𝗨𝗻𝗸𝗻𝗼𝘄𝗻"]


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

    processing_message = await message.reply("🔍 **𝑺𝒄𝒂𝒏𝒏𝒊𝒏𝒈 𝒕𝒉𝒆 𝒘𝒆𝒃𝒔𝒊𝒕𝒆... 𝑷𝒍𝒆𝒂𝒔𝒆 𝒘𝒂𝒊𝒕...**", disable_web_page_preview=True)

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
    cloudflare = "✅ 𝗘𝗻𝗮𝗯𝗹𝗲𝗱" if data['cloudflare_protected'] else "🚫 𝗡𝗼𝘁 𝗘𝗻𝗮𝗯𝗹𝗲𝗱"

    result_message = format_message(
        f"🌐 **𝗦𝗶𝘁𝗲:** `{website_url}`\n"
        f"💳 **𝗣𝗮𝘆𝗺𝗲𝗻𝘁 𝗚𝗮𝘁𝗲𝘄𝗮𝘆𝘀:** `{gateways}`\n"
        f"🔒 **𝗖𝗮𝗽𝘁𝗰𝗵𝗮:** `{captcha}`\n"
        f"☁️ **𝗖𝗹𝗼𝘂𝗱𝗳𝗹𝗮𝗿𝗲:** `{cloudflare}`\n"
    )

    await processing_message.edit_text(result_message, disable_web_page_preview=True)


if __name__ == "__main__":
    print("🤖 Bot is running...")
    app.run()
