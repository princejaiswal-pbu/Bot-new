"""
Optimized Bot Handlers for Telegram Bot
Author: AI Assistant
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from config import OWNER_IDS
from database import DatabaseManager
from qr_code import QRCodeManager
from utils import format_product_message, send_typing_action

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
        self.qr_manager = QRCodeManager()
        self._init_default_data()

    def _init_default_data(self):
        """Initialize default data if not exists"""
        if not self.db.get_setting('bio_message'):
            default_bio = (
                "🚀 *Welcome to Premium Digital Store!* 🚀\n\n"
                "🎯 Get premium apps & tools\n"
                "💎 Quality guaranteed products\n"
                "⚡ Instant delivery after payment\n"
                "🛡️ 100% secure transactions\n\n"
                "💬 Contact: @Abdul20298"
            )
            self.db.set_setting('bio_message', default_bio)

        # Initialize default products
        if not self.db.get_all_products():
            self.db.add_product(
                "Diuwin", "Diuwin Premium", 
                "Premium features, Ad-free experience, Priority support",
                "299", "Complete premium access to Diuwin application"
            )
            self.db.add_product(
                "Cricket 24", "Cricket 24 Pro", 
                "Live scores, Premium stats, Ad-free viewing",
                "199", "Professional cricket tracking and statistics"
            )

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update.effective_user or not update.message:
            return

        user = update.effective_user
        
        # Add typing action for better UX
        asyncio.create_task(send_typing_action(context, user.id, 1.0))

        # Add user to database with safe handling
        try:
            self.db.add_user(
                user.id, 
                user.username or f"user_{user.id}", 
                user.first_name or "Unknown",
                user.last_name or ""
            )
            
            # Update activity
            self.db.update_user_activity(user.id)
        except Exception as e:
            logger.error(f"Error adding user {user.id}: {e}")

        # Check if user is owner/admin
        if user.id in OWNER_IDS:
            if user.username:
                welcome_text = f"👑 Welcome back, Owner @{user.username}!"
            else:
                welcome_text = f"👑 Welcome back, Owner!"
        else:
            welcome_text = f"👋 Welcome {user.first_name}!"

        # Get bio message
        bio_message = self.db.get_setting('bio_message', 'Welcome to our store!')
        
        # Create keyboard
        keyboard = [
            [InlineKeyboardButton("💎 Premium Files", callback_data="premium_files")]
        ]
        
        # Add admin panel button for admins
        if self.db.is_admin(user.id) or user.id in OWNER_IDS:
            keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            f"{welcome_text}\n\n{bio_message}",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def premium_files_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle premium files button"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        
        # Add typing action
        asyncio.create_task(send_typing_action(context, query.from_user.id, 0.5))
        
        # Update user activity
        self.db.update_user_activity(query.from_user.id)
        
        # Get unique categories
        products = self.db.get_all_products()
        categories = list(set(product['category'] for product in products))
        
        if not categories:
            await query.edit_message_text(
                "🚫 No products available at the moment.\n\nPlease check back later!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Main", callback_data="back_to_main")]
                ])
            )
            return
        
        keyboard = []
        for category in categories:
            keyboard.append([InlineKeyboardButton(f"📁 {category}", callback_data=f"category_{category}")])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back to Main", callback_data="back_to_main")])
        
        await query.edit_message_text(
            "💎 *Premium Digital Products*\n\n"
            "Choose a category to explore our premium collection:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def category_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle category selection"""
        query = update.callback_query
        if not query or not query.from_user or not query.data:
            return
            
        await query.answer()
        
        category = query.data.replace("category_", "")
        products = self.db.get_products_by_category(category)
        
        if not products:
            await query.edit_message_text(
                f"🚫 No products found in {category} category.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back to Categories", callback_data="premium_files")]
                ])
            )
            return
        
        keyboard = []
        for product in products:
            keyboard.append([InlineKeyboardButton(
                f"🎯 {product['name']} - ₹{product['price']}", 
                callback_data=f"product_{product['id']}"
            )])
        
        keyboard.append([InlineKeyboardButton("⬅️ Back to Categories", callback_data="premium_files")])
        
        await query.edit_message_text(
            f"📁 *{category} Products*\n\n"
            f"Available products in this category:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def product_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle specific product selection"""
        query = update.callback_query
        if not query or not query.from_user or not query.data:
            return
            
        await query.answer()
        
        product_id = int(query.data.replace("product_", ""))
        products = self.db.get_all_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            await query.edit_message_text(
                "❌ Product not found!",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back", callback_data="premium_files")]
                ])
            )
            return
        
        await self.show_product_details(query, product)

    async def show_product_details(self, query, product):
        """Show detailed product information"""
        product_message = format_product_message(product)
        
        keyboard = [
            [InlineKeyboardButton("💳 Buy Now", callback_data=f"buy_{product['id']}")],
            [InlineKeyboardButton("⬅️ Back to Products", callback_data=f"category_{product['category']}")]
        ]
        
        await query.edit_message_text(
            product_message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def buy_now_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle buy now button"""
        query = update.callback_query
        if not query or not query.from_user or not query.data:
            return
            
        await query.answer()
        
        product_id = int(query.data.replace("buy_", ""))
        products = self.db.get_all_products()
        product = next((p for p in products if p['id'] == product_id), None)
        
        if not product:
            await query.edit_message_text("❌ Product not found!")
            return
        
        # Add order to database
        self.db.add_order(query.from_user.id, product['name'], product['price'])
        
        # Send payment instructions
        payment_message = self.qr_manager.create_payment_qr_message(product['price'])
        
        keyboard = [
            [InlineKeyboardButton("📸 Upload Screenshot", callback_data=f"upload_screenshot_{product_id}")],
            [InlineKeyboardButton("🏠 Main Menu", callback_data="back_to_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send QR code if exists
        if self.qr_manager.qr_code_exists():
            try:
                with open(self.qr_manager.get_qr_code_path(), 'rb') as qr_file:
                    await query.message.reply_photo(
                        photo=qr_file,
                        caption=payment_message,
                        reply_markup=reply_markup,
                        parse_mode='Markdown'
                    )
                    # Delete original message to avoid clutter
                    await query.delete_message()
            except Exception as e:
                logger.error(f"Error sending QR code: {e}")
                await query.edit_message_text(
                    payment_message,
                    reply_markup=reply_markup,
                    parse_mode='Markdown'
                )
        else:
            await query.edit_message_text(
                payment_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )

    async def back_to_main_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle back to main menu"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        
        user = query.from_user
        bio_message = self.db.get_setting('bio_message', 'Welcome to our store!')
        
        # Create main menu keyboard
        keyboard = [
            [InlineKeyboardButton("💎 Premium Files", callback_data="premium_files")]
        ]
        
        # Add admin panel button for admins
        if self.db.is_admin(user.id) or user.id in OWNER_IDS:
            keyboard.append([InlineKeyboardButton("⚙️ Admin Panel", callback_data="admin_panel")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            bio_message,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo uploads (payment screenshots)"""
        if not update.message or not update.effective_user:
            return
            
        user = update.effective_user
        
        # Add typing action
        asyncio.create_task(send_typing_action(context, user.id, 1.0))
        
        # Get the largest photo
        photo = update.message.photo[-1]
        file_id = photo.file_id
        
        # Save screenshot reference in database
        try:
            # Update the latest order with screenshot
            self.db.add_order(user.id, "Screenshot Upload", "0", file_id)
            
            await update.message.reply_text(
                "✅ *Payment Screenshot Received!*\n\n"
                "📋 Your payment will be verified within 24 hours\n"
                "📞 Contact: @Abdul20298 for any queries\n"
                "🔔 You'll be notified once verified",
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error saving screenshot: {e}")
            await update.message.reply_text(
                "❌ Error processing screenshot. Please try again or contact @Abdul20298",
                parse_mode='Markdown'
            )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        if not update.message or not update.effective_user:
            return
            
        user = update.effective_user
        
        # Add user if not exists
        try:
            self.db.add_user(
                user.id, 
                user.username or f"user_{user.id}", 
                user.first_name or "Unknown",
                user.last_name or ""
            )
        except Exception as e:
            logger.error(f"Error handling message from {user.id}: {e}")
        
        # Simple response for general messages
        await update.message.reply_text(
            "👋 Hello! Use /start to see available options.",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Get Started", callback_data="back_to_main")]
            ])
        )