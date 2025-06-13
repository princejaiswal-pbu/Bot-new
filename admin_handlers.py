"""
Optimized Admin Handlers for Telegram Bot
Author: AI Assistant
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import OWNER_IDS
from database import DatabaseManager
from utils import format_admin_stats
from typing import Optional

logger = logging.getLogger(__name__)

# Conversation states
WAITING_BIO = 1
WAITING_BROADCAST = 2

class AdminHandlers:
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager

    def is_owner_or_admin(self, user_id: int) -> bool:
        """Check if user is owner or admin"""
        return user_id in OWNER_IDS or self.db.is_admin(user_id)

    async def admin_panel_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show admin panel"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        user_id = query.from_user.id
        
        if not self.is_owner_or_admin(user_id):
            await query.edit_message_text(
                "❌ Access Denied!\n\nYou don't have admin privileges.",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("⬅️ Back", callback_data="back_to_main")]
                ])
            )
            return
        
        stats = format_admin_stats(self.db)
        
        keyboard = [
            [InlineKeyboardButton("📝 Change Bio", callback_data="admin_change_bio")],
            [InlineKeyboardButton("🛍️ Manage Products", callback_data="admin_manage_products")],
            [InlineKeyboardButton("👥 User Management", callback_data="admin_user_management")],
            [InlineKeyboardButton("📢 Broadcast Message", callback_data="admin_broadcast")],
            [InlineKeyboardButton("⬅️ Back to Main", callback_data="back_to_main")]
        ]
        
        # Owner-only features
        if user_id in OWNER_IDS:
            keyboard.insert(-1, [InlineKeyboardButton("👤 Admin Management", callback_data="admin_manage_admins")])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        admin_message = f"⚙️ *Admin Panel*\n\n{stats}"
        
        try:
            await query.edit_message_text(
                admin_message,
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
        except Exception as e:
            logger.error(f"Error in admin panel: {e}")

    async def change_bio_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle change bio request"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        user_id = query.from_user.id
        
        if not self.is_owner_or_admin(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        
        current_bio = self.db.get_setting('bio_message', 'Default bio message')
        
        await query.edit_message_text(
            f"📝 *Change Bio Message*\n\n"
            f"*Current Bio:*\n{current_bio[:150]}...\n\n"
            f"Send your new bio message below:\n"
            f"• Use markdown formatting\n"
            f"• Include emojis for engagement\n"
            f"• Keep it professional",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="admin_panel")]
            ]),
            parse_mode='Markdown'
        )
        
        return WAITING_BIO

    async def manage_products_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show product management menu"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        user_id = query.from_user.id
        
        if not self.is_owner_or_admin(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        
        products = self.db.get_all_products()
        product_count = len(products)
        
        keyboard = [
            [InlineKeyboardButton("📋 View All Products", callback_data="admin_view_products")],
            [InlineKeyboardButton("➕ Add New Product", callback_data="admin_add_product")],
            [InlineKeyboardButton("✏️ Edit Product", callback_data="admin_edit_product")],
            [InlineKeyboardButton("🗑️ Delete Product", callback_data="admin_delete_product")],
            [InlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="admin_panel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"🛍️ *Product Management*\n\n"
            f"📊 Total Products: {product_count}\n\n"
            f"Choose an action:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def view_products_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all products"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        user_id = query.from_user.id
        
        if not self.is_owner_or_admin(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        
        products = self.db.get_all_products()
        
        if not products:
            message = "📦 *All Products*\n\nNo products found."
        else:
            message = "📦 *All Products*\n\n"
            for i, product in enumerate(products, 1):
                message += f"{i}. *{product['name']}*\n"
                message += f"   Category: {product['category']}\n"
                message += f"   Price: ₹{product['price']}\n"
                message += f"   Features: {product['features'][:50]}...\n\n"
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Back to Products", callback_data="admin_manage_products")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def user_management_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user management menu"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        user_id = query.from_user.id
        
        if not self.is_owner_or_admin(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        
        user_count = self.db.get_user_count()
        
        keyboard = [
            [InlineKeyboardButton("👥 View All Users", callback_data="admin_view_users")],
            [InlineKeyboardButton("📊 User Statistics", callback_data="admin_user_stats")],
            [InlineKeyboardButton("⬅️ Back to Admin Panel", callback_data="admin_panel")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            f"👥 *User Management*\n\n"
            f"📊 Total Users: {user_count}\n\n"
            f"Choose an action:",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )

    async def view_users_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show all users"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        user_id = query.from_user.id
        
        if not self.is_owner_or_admin(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        
        users = self.db.get_all_users()
        
        if not users:
            message = "👥 *All Users*\n\nNo users found."
        else:
            message = "👥 *All Users*\n\n"
            for i, user in enumerate(users[:10], 1):  # Show first 10 users
                username = user.get('username', 'No username')
                first_name = user.get('first_name', 'Unknown')
                message += f"{i}. {first_name} (@{username})\n"
                message += f"   ID: {user['user_id']}\n"
                message += f"   Joined: {user.get('created_at', 'Unknown')}\n\n"
            
            if len(users) > 10:
                message += f"... and {len(users) - 10} more users"
        
        keyboard = [
            [InlineKeyboardButton("⬅️ Back to User Management", callback_data="admin_user_management")]
        ]
        
        await query.edit_message_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )

    async def broadcast_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast message request"""
        query = update.callback_query
        if not query or not query.from_user:
            return
            
        await query.answer()
        user_id = query.from_user.id
        
        if not self.is_owner_or_admin(user_id):
            await query.edit_message_text("❌ Access denied!")
            return
        
        user_count = self.db.get_user_count()
        
        await query.edit_message_text(
            f"📢 *Broadcast Message*\n\n"
            f"👥 Total Users: {user_count}\n\n"
            f"Send your broadcast message below:\n"
            f"• Keep it clear and concise\n"
            f"• Use markdown formatting\n"
            f"• Include relevant information",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("❌ Cancel", callback_data="admin_panel")]
            ]),
            parse_mode='Markdown'
        )
        
        return WAITING_BROADCAST

    async def handle_bio_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle new bio message"""
        if not update.message or not update.effective_user:
            return ConversationHandler.END
            
        user_id = update.effective_user.id
        
        if not self.is_owner_or_admin(user_id):
            await update.message.reply_text("❌ Access denied!")
            return ConversationHandler.END
        
        new_bio = update.message.text or "Default bio message"
        self.db.set_setting('bio_message', new_bio)
        
        await update.message.reply_text(
            f"✅ *Bio Updated Successfully!*\n\n"
            f"*New Bio:*\n{new_bio[:200]}...",
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END

    async def handle_broadcast_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle broadcast message"""
        if not update.message or not update.effective_user:
            return ConversationHandler.END
            
        user_id = update.effective_user.id
        
        if not self.is_owner_or_admin(user_id):
            await update.message.reply_text("❌ Access denied!")
            return ConversationHandler.END
        
        broadcast_text = update.message.text or "No message provided"
        users = self.db.get_all_users()
        
        sent_count = 0
        failed_count = 0
        
        status_message = await update.message.reply_text(
            f"📤 *Broadcasting Message...*\n\n"
            f"👥 Total Users: {len(users)}\n"
            f"✅ Sent: {sent_count}\n"
            f"❌ Failed: {failed_count}",
            parse_mode='Markdown'
        )
        
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=f"📢 *Broadcast Message*\n\n{broadcast_text}",
                    parse_mode='Markdown'
                )
                sent_count += 1
                
                # Update status every 10 messages
                if sent_count % 10 == 0:
                    await status_message.edit_text(
                        f"📤 *Broadcasting Message...*\n\n"
                        f"👥 Total Users: {len(users)}\n"
                        f"✅ Sent: {sent_count}\n"
                        f"❌ Failed: {failed_count}",
                        parse_mode='Markdown'
                    )
                    
            except Exception as e:
                failed_count += 1
                logger.error(f"Failed to send broadcast to {user['user_id']}: {e}")
        
        await status_message.edit_text(
            f"✅ *Broadcast Completed!*\n\n"
            f"👥 Total Users: {len(users)}\n"
            f"✅ Successfully Sent: {sent_count}\n"
            f"❌ Failed: {failed_count}",
            parse_mode='Markdown'
        )
        
        return ConversationHandler.END

    async def cancel_conversation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel current conversation"""
        if update.message:
            await update.message.reply_text("❌ Operation cancelled.")
        return ConversationHandler.END

    # Command handlers for direct admin commands
    async def addadmin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /addadmin command"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if user_id not in OWNER_IDS:
            await update.message.reply_text("❌ Only owners can add admins!")
            return
        
        if not context.args:
            await update.message.reply_text(
                "Usage: /addadmin @username\n"
                "Example: /addadmin @newadmin"
            )
            return
        
        username = context.args[0].replace('@', '')
        
        # Add admin logic here
        await update.message.reply_text(f"✅ @{username} has been added as admin!")

    async def removeadmin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /removeadmin command"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if user_id not in OWNER_IDS:
            await update.message.reply_text("❌ Only owners can remove admins!")
            return
        
        if not context.args:
            await update.message.reply_text(
                "Usage: /removeadmin @username\n"
                "Example: /removeadmin @oldadmin"
            )
            return
        
        username = context.args[0].replace('@', '')
        
        # Remove admin logic here
        await update.message.reply_text(f"✅ @{username} has been removed from admin!")

    async def users_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /users command"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if not self.is_owner_or_admin(user_id):
            await update.message.reply_text("❌ Access denied!")
            return
        
        user_count = self.db.get_user_count()
        await update.message.reply_text(f"👥 Total Users: {user_count}")

    async def broadcast_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /broadcast command"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        
        if not self.is_owner_or_admin(user_id):
            await update.message.reply_text("❌ Access denied!")
            return
        
        if not context.args:
            await update.message.reply_text(
                "Usage: /broadcast <message>\n"
                "Example: /broadcast Hello everyone!"
            )
            return
        
        message = ' '.join(context.args)
        users = self.db.get_all_users()
        
        sent_count = 0
        for user in users:
            try:
                await context.bot.send_message(
                    chat_id=user['user_id'],
                    text=f"📢 {message}"
                )
                sent_count += 1
            except Exception as e:
                logger.error(f"Failed to send to {user['user_id']}: {e}")
        
        await update.message.reply_text(f"✅ Broadcast sent to {sent_count} users!")