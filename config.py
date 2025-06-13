import os

# Bot Configuration
BOT_TOKEN = "7932661982:AAFRBaucYAh9wmnnWxEllc01t0DMbr1rBIo"
OWNER_USERNAMES = ["Abdul20298", "Smile_Bot123"]
OWNER_IDS = []  # Will be populated when owners first interact

# Database Configuration
DATABASE_PATH = "bot_database.db"

# Default Messages
DEFAULT_BIO = """👋 Welcome to Premium Digital Files Store!
🚀 Get the most powerful tools at your fingertips.
💼 Premium Files Just 1 Click Away!"""

DEFAULT_PAYMENT_MESSAGE = """🧾 Scan the QR to Pay  
📸 Send payment screenshot after completing  
📞 Contact Owner: @Abdul20298"""

# Product Categories
DEFAULT_CATEGORIES = ["🔹 Diuwin", "🔸 Cricket 24"]

# Default Products
DEFAULT_PRODUCTS = {
    "Diuwin": {
        "name": "🔹 Diuwin Premium",
        "features": "✨ Advanced Features\n🎯 High Performance\n🔒 Secure Access\n💯 24/7 Support",
        "price": "₹299",
        "description": "Get premium access to Diuwin platform with exclusive features!"
    },
    "Cricket 24": {
        "name": "🔸 Cricket 24 Pro",
        "features": "🏏 Live Updates\n📊 Advanced Stats\n🎯 Premium Analysis\n📱 Mobile Optimized",
        "price": "₹199",
        "description": "Professional cricket analysis and live updates platform!"
    }
}
