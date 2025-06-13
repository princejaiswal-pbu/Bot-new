import os
from PIL import Image, ImageDraw, ImageFont
import io
from typing import Optional, Union

class QRCodeManager:
    def __init__(self):
        self.qr_file_path = "static/qr_payment.jpg"
    
    def get_qr_code_path(self) -> str:
        """Get QR code file path"""
        return self.qr_file_path
    
    def qr_code_exists(self) -> bool:
        """Check if QR code file exists"""
        return os.path.exists(self.qr_file_path)
    
    def save_qr_code(self, file_content: bytes, file_extension: str = 'jpg') -> bool:
        """Save uploaded QR code file"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(self.qr_file_path), exist_ok=True)
            
            # Save as JPG for now (can be extended for other formats)
            file_path = self.qr_file_path.replace('.jpg', f'.{file_extension}')
            
            with open(file_path, 'wb') as f:
                f.write(file_content)
            
            self.qr_file_path = file_path
            return True
        except Exception as e:
            print(f"Error saving QR code: {e}")
            return False
    
    def create_payment_qr_message(self, amount: Optional[str] = None) -> str:
        """Create payment message with QR code instructions"""
        message = "💳 **Payment Instructions**\n\n"
        message += "🧾 Scan the QR code below to pay\n"
        if amount:
            message += f"💰 Amount: {amount}\n"
        message += "📸 Send payment screenshot after completing\n"
        message += "📞 Contact Owner: @Abdul20298\n\n"
        message += "⚡ Payment will be verified within 24 hours"
        
        return message
