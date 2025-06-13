# Telegram Bot - Digital Product Sales

Complete Python bot for selling digital products with admin panel and payment integration.

## Quick Setup for Hosting

### For Heroku:
1. Upload this folder as zip
2. Set BOT_TOKEN environment variable
3. Deploy as worker dyno

### For Railway/Render:
1. Upload project files
2. Set BOT_TOKEN in environment
3. Use `python main.py` as start command

### For VPS/Cloud:
```bash
pip install -r requirements.txt
python main.py
```

## Environment Variables Required:
- `BOT_TOKEN` - Your Telegram bot token

## Features:
- Dual owner system (@Abdul20298 & @Smile_Bot123)
- Product catalog with QR payment
- Admin panel with broadcast
- SQLite database (auto-created)
- File upload support

## Files Structure:
- `main.py` - Main bot application
- `config.py` - Configuration settings
- `bot_handlers.py` - User interactions
- `admin_handlers.py` - Admin functions
- `database.py` - Database management
- `utils.py` - Helper functions
- `qr_code.py` - Payment QR management
- `static/` - QR code images
- `requirements.txt` - Dependencies

## Support:
Contact @Abdul20298 for any issues.