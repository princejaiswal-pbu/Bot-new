import asyncio
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from typing import List, Dict
import re

def create_inline_keyboard(buttons: List[List[Dict[str, str]]]) -> InlineKeyboardMarkup:
    """Create inline keyboard from button configuration"""
    keyboard = []
    for row in buttons:
        keyboard_row = []
        for button in row:
            keyboard_row.append(InlineKeyboardButton(
                text=button['text'],
                callback_data=button['callback_data']
            ))
        keyboard.append(keyboard_row)
    
    return InlineKeyboardMarkup(keyboard)

def format_user_info(user) -> str:
    """Format user information for display"""
    username = f"@{user.username}" if user.username else "No username"
    name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    return f"👤 {name}\n🔗 {username}\n🆔 {user.id}"

def validate_username(username: str) -> bool:
    """Validate Telegram username format"""
    pattern = r'^@?[a-zA-Z0-9_]{5,32}$'
    return bool(re.match(pattern, username))

def escape_markdown(text: str) -> str:
    """Escape markdown special characters"""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    return text

def chunk_list(lst: list, chunk_size: int) -> List[list]:
    """Split list into chunks of specified size"""
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]

async def send_typing_action(context, chat_id: int, duration: float = 1.0):
    """Send typing action for specified duration"""
    await context.bot.send_chat_action(chat_id=chat_id, action='typing')
    await asyncio.sleep(duration)

def format_product_message(product: Dict) -> str:
    """Format product information for display"""
    return f"""
🛍️ **{product['name']}**

✨ **Features:**
{product['features']}

💰 **Price:** {product['price']}

📝 **Description:**
{product['description']}
"""

def format_admin_stats(db_manager) -> str:
    """Format admin statistics"""
    user_count = db_manager.get_user_count()
    product_count = len(db_manager.get_all_products())
    
    return f"""
📊 **Bot Statistics**

👥 Total Users: {user_count}
🛍️ Total Products: {product_count}
🤖 Bot Status: Active
"""

def is_owner(user_id: int, username: str = None) -> bool:
    """Check if user is one of the bot owners"""
    from config import OWNER_IDS, OWNER_USERNAMES
    
    # Check by user ID if available
    if user_id in OWNER_IDS:
        return True
    
    # Check by username if provided
    if username and username.replace('@', '') in OWNER_USERNAMES:
        return True
    
    return False
