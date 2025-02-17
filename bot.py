import requests
import textwrap
import re
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# ☫ Bot Configuration
API_ID = 22318470  # ☫ Replace with your API ID
API_HASH = "cf907c4c2d677b9f67d32828d891e97a"  # ☫ Replace with your API Hash
BOT_TOKEN = "7289532935:AAElv5h7xisIMuaiaw8wkYlcB-Od1HKjrdQ"  # ☫ Replace with your Bot Token
OWNER_ID = 7222795580  # ☫ Replace with your Telegram user ID

# ☫ Initialize Pyrogram Bot
app = Client("PaymentGatewayBot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# ☫ Database to track stats and registrations
stats = {"total_users": set(), "sites_checked": 0}
registered_users = set()

def format_message(content):
    return textwrap.fill(content, width=50)

def fetch_website_data(url):
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except requests.RequestException:
        return None

def detect_payment_gateways(response_text):
    gateways = {
        "paypal": "PayPal", "stripe": "Stripe", "braintree": "Braintree",
        "square": "Square", "authorize.net": "Authorize.Net", "razorpay": "Razorpay",
        "adyen": "Adyen", "payu": "PayU", "worldpay": "WorldPay",
        "skrill": "Skrill", "payoneer": "Payoneer", "paytm": "Paytm",
        "wepay": "WePay", "klarna": "Klarna", "afterpay": "Afterpay",
        "alipay": "Alipay", "unionpay": "UnionPay", "amazonpay": "Amazon Pay",
        "applepay": "Apple Pay", "googlepay": "Google Pay",
    }
    return [name for key, name in gateways.items() if key in response_text.lower()] or ["No Payment Gateways Detected"]

def detect_captcha(response_text):
    if "recaptcha" in response_text.lower():
        return "Google reCAPTCHA ✅"
    elif "hcaptcha" in response_text.lower():
        return "hCaptcha ✅"
    return "No Captcha Detected ❌"

def detect_cloudflare(response_text):
    cloudflare_indicators = ["cloudflare.com", "__cfduid", "cf-ray", "cf-cache-status"]
    return "Enabled ✅" if any(indicator in response_text.lower() for indicator in cloudflare_indicators) else "Not Enabled ❌"

def detect_payment_type(response_text):
    if "3d secure" in response_text.lower() or "stripe3dsecure" in response_text.lower():
        return "3D Secure Payment ✅"
    elif "stripe-checkout" in response_text.lower() or "2d secure" in response_text.lower():
        return "2D Payment ❌"
    return "Unknown Payment Type ⚠️"

@app.on_message(filters.command("start"))
async def start(client, message):
    user = message.from_user
    start_msg = (
        f"☫ Welcome {user.first_name}!\n\n"
        "☫ Register with /register to use the bot.\n\n"
        "☫ Analyze payment gateways, captchas, security measures, and Cloudflare protection on websites.\n\n"
        "☫ Join [@PhiloBots](https://t.me/PhiloBots) for More Tools!"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("☫ Register", callback_data="register"),
         InlineKeyboardButton("☫ Stats", callback_data="stats")],
        [InlineKeyboardButton("☫ Join @PhiloBots", url="https://t.me/PhiloBots")]
    ])
    await message.reply(start_msg, reply_markup=keyboard)

@app.on_message(filters.command("register"))
async def register(client, message):
    user_id = message.from_user.id
    if user_id in registered_users:
        await message.reply("☫ You are already registered.")
    else:
        registered_users.add(user_id)
        stats["total_users"].add(user_id)
        await message.reply("☫ Registration successful! Now you can use the bot.")

@app.on_message(filters.command("stats"))
async def stats_command(client, message):
    await message.reply(f"☫ Total Registered Users: {len(stats['total_users'])}\n☫ Total Sites Checked: {stats['sites_checked']}")

@app.on_message(filters.text & ~filters.command(["start", "profile", "stats", "register", "help"]))
async def auto_check_site(client, message):
    user_id = message.from_user.id
    if user_id not in registered_users:
        await message.reply("☫ Please register with /register before using the bot.")
        return

    stats["sites_checked"] += 1
    urls = re.findall(r'https?://\S+', message.text)
    if not urls:
        return

    website_url = urls[0]
    processing_message = await message.reply("☫ Scanning... Please wait...", disable_web_page_preview=True)
    response_text = fetch_website_data(website_url)

    if not response_text:
        await processing_message.edit_text("☫ Error: Could not retrieve details. Ensure the website is reachable.")
        return

    result_message = (
        f"☫ Scanned: {website_url}\n"
        f"☫ Payment Gateways: {', '.join(detect_payment_gateways(response_text))}\n"
        f"☫ Captcha: {detect_captcha(response_text)}\n"
        f"☫ Cloudflare Protection: {detect_cloudflare(response_text)}\n"
        f"☫ Payment Type: {detect_payment_type(response_text)}\n"
        f"☫ Checked by: {message.from_user.first_name}"
    )
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("☫ Recheck", callback_data=f"recheck_{website_url}")],
        [InlineKeyboardButton("☫ Join @PhiloBots", url="https://t.me/PhiloBots")]
    ])
    await processing_message.edit_text(result_message, disable_web_page_preview=True, reply_markup=keyboard)

if __name__ == "__main__":
    print("☫ Bot is running...")
    app.run()
