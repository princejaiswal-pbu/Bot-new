"""
Optimized Telegram Bot for Digital Product Sales
Author: AI Assistant
"""

import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler, 
    MessageHandler, filters, ConversationHandler
)
from config import BOT_TOKEN
from database import DatabaseManager
from bot_handlers import BotHandlers
from admin_handlers import AdminHandlers, WAITING_BIO, WAITING_BROADCAST

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class DigitalProductBot:
    def __init__(self):
        self.db = DatabaseManager('bot_database.db')
        self.bot_handlers = BotHandlers(self.db)
        self.admin_handlers = AdminHandlers(self.db)
        self.application = None

    def setup_handlers(self):
        """Setup all bot handlers"""
        app = self.application
        
        # Basic command handlers
        app.add_handler(CommandHandler("start", self.bot_handlers.start_command))
        
        # Admin command handlers
        app.add_handler(CommandHandler("addadmin", self.admin_handlers.addadmin_command))
        app.add_handler(CommandHandler("removeadmin", self.admin_handlers.removeadmin_command))
        app.add_handler(CommandHandler("users", self.admin_handlers.users_command))
        app.add_handler(CommandHandler("broadcast", self.admin_handlers.broadcast_command))
        
        # Conversation handlers for admin operations
        bio_conversation = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.admin_handlers.change_bio_callback, pattern="^admin_change_bio$")],
            states={
                WAITING_BIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_handlers.handle_bio_message)]
            },
            fallbacks=[
                CallbackQueryHandler(self.admin_handlers.cancel_conversation, pattern="^admin_panel$"),
                CommandHandler("cancel", self.admin_handlers.cancel_conversation)
            ],
            per_message=False
        )
        
        broadcast_conversation = ConversationHandler(
            entry_points=[CallbackQueryHandler(self.admin_handlers.broadcast_callback, pattern="^admin_broadcast$")],
            states={
                WAITING_BROADCAST: [MessageHandler(filters.TEXT & ~filters.COMMAND, self.admin_handlers.handle_broadcast_message)]
            },
            fallbacks=[
                CallbackQueryHandler(self.admin_handlers.cancel_conversation, pattern="^admin_panel$"),
                CommandHandler("cancel", self.admin_handlers.cancel_conversation)
            ],
            per_message=False
        )
        
        app.add_handler(bio_conversation)
        app.add_handler(broadcast_conversation)
        
        # Main callback handlers
        app.add_handler(CallbackQueryHandler(self.admin_handlers.admin_panel_callback, pattern="^admin_panel$"))
        app.add_handler(CallbackQueryHandler(self.admin_handlers.manage_products_callback, pattern="^admin_manage_products$"))
        app.add_handler(CallbackQueryHandler(self.admin_handlers.view_products_callback, pattern="^admin_view_products$"))
        app.add_handler(CallbackQueryHandler(self.admin_handlers.user_management_callback, pattern="^admin_user_management$"))
        app.add_handler(CallbackQueryHandler(self.admin_handlers.view_users_callback, pattern="^admin_view_users$"))
        
        # Bot callback handlers
        app.add_handler(CallbackQueryHandler(self.bot_handlers.premium_files_callback, pattern="^premium_files$"))
        app.add_handler(CallbackQueryHandler(self.bot_handlers.category_callback, pattern="^category_"))
        app.add_handler(CallbackQueryHandler(self.bot_handlers.product_callback, pattern="^product_"))
        app.add_handler(CallbackQueryHandler(self.bot_handlers.buy_now_callback, pattern="^buy_"))
        app.add_handler(CallbackQueryHandler(self.bot_handlers.back_to_main_callback, pattern="^back_to_main$"))
        
        # Generic callback handlers for unhandled callbacks
        app.add_handler(CallbackQueryHandler(self.handle_unknown_callback))
        
        # Message handlers
        app.add_handler(MessageHandler(filters.PHOTO, self.bot_handlers.handle_photo))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.bot_handlers.handle_message))
        
        # Error handler
        app.add_error_handler(self.error_handler)

    async def handle_unknown_callback(self, update: Update, context):
        """Handle unknown callback queries"""
        query = update.callback_query
        if query:
            await query.answer("⚠️ This action is not available.")

    async def error_handler(self, update: Update, context):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        # Try to respond to user if possible
        if update and update.effective_chat:
            try:
                await context.bot.send_message(
                    chat_id=update.effective_chat.id,
                    text="❌ An error occurred. Please try again or contact @Abdul20298"
                )
            except Exception as e:
                logger.error(f"Could not send error message: {e}")

    async def start_bot(self):
        """Start the bot"""
        logger.info("Starting Digital Product Sales Bot...")
        
        # Initialize database
        self.db.init_database()
        
        # Create application with optimized settings
        self.application = (
            Application.builder()
            .token(BOT_TOKEN)
            .concurrent_updates(True)
            .rate_limiter(None)
            .build()
        )
        
        # Setup handlers
        self.setup_handlers()
        
        # Start polling with optimized settings
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling(
            poll_interval=1.0,
            timeout=10,
            drop_pending_updates=True,
            allowed_updates=['message', 'callback_query']
        )
        
        logger.info("Bot is running... Press Ctrl+C to stop.")

    async def stop_bot(self):
        """Stop the bot gracefully"""
        if self.application:
            await self.application.stop()
        logger.info("Bot stopped.")

def main():
    """Main function"""
    bot = DigitalProductBot()
    
    try:
        # Run the bot
        asyncio.run(bot.start_bot())
    except KeyboardInterrupt:
        logger.info("Received interrupt signal, stopping bot...")
        asyncio.run(bot.stop_bot())
    except Exception as e:
        logger.error(f"Fatal error: {e}")

if __name__ == "__main__":
    main()