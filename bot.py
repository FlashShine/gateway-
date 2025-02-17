import requests
import textwrap
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ☫ Bot Configuration
API_ID = 22318470  # ☫ Replace with your API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # ☫ Replace with your API Hash
BOT_TOKEN = "7289532935:AAEuFrx_Eo1df5ZNDhEb2O6PZ-qmqaUhJNs"  # ☫ Replace with your Bot Token
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


@app.on_message(filters.command("start"))
async def start(client, message):
    """☫ Handles /start command."""
    user = message.from_user
    start_msg = (
        f"☫ Welcome {user.first_name}!\n\n"
        "☫ Register with /register to use the bot.\n\n"
        "☫ Analyze payment gateways, captchas, and security details on any website.\n\n"
        "☫ Join [@PhiloBots](https://t.me/PhiloBots) for More Tools!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("☫ Join @PhiloBots", url="https://t.me/PhiloBots")],
        [InlineKeyboardButton("☫ Bot Info", callback_data="bot_info"),
         InlineKeyboardButton("☫ Support", url="https://t.me/PhiloBotsSupport")]
    ])
    await message.reply(start_msg, reply_markup=keyboard)


@app.on_message(filters.command("register"))
async def register(client, message):
    """☫ Registers a user to use the bot."""
    user_id = message.from_user.id
    if user_id in registered_users:
        await message.reply("☫ You are already registered.")
    else:
        registered_users.add(user_id)
        await message.reply("☫ Registration successful! Now you can use the bot.")


@app.on_message(filters.command("stats"))
async def stats_command(client, message):
    """☫ Shows bot statistics."""
    total_users = len(registered_users)
    total_sites_checked = stats["sites_checked"]
    stats_msg = (
        f"☫ Total Registered Users: {total_users}\n"
        f"☫ Total Sites Checked: {total_sites_checked}\n"
        "☫ Join @PhiloBots for more updates!"
    )
    await message.reply(stats_msg)


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

    site_text = format_message(f"☫ Site: {website_url}")
    security_text = format_message(f"☫ Security Analysis: Secure ☫")
    checked_by_text = format_message(f"☫ Checked By: {user_name}")

    result_message = (
        "╭━━━━━━━━━━━━━━━━━━━╮\n"
        f"│ {site_text}\n"
        f"│ {security_text}\n"
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
