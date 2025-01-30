# src/conversions.py

import json
import base64
import binascii
from typing import Dict, Any
from .utils import ValidationError, validate_json, safe_json_loads

class CryptoConverter:
    """
    Handles cryptographic conversions between hex, ASCII, and unknown formats.
    """
    
    CHUNK_SIZE = 32  # Size for JSON string chunking
    HEADER = "d8ab19d5c7a0f27c10fa57540506ac68"
    XOR_KEY = 0xD8
    OFFSET_MOD = 16  # Based on 32-character chunk hint (32 chars = 16 bytes)
    
    def __init__(self, debug=False):
        self._debug = debug

    def analyze_pattern(self, hex_str: str, unknown_str: str):
        """Utility method to analyze transformation patterns."""
        hex_bytes = bytes.fromhex(hex_str)
        unknown_bytes = bytes.fromhex(unknown_str)
        
        print("Pattern Analysis:")
        for i in range(min(self.CHUNK_SIZE, len(hex_bytes))):
            h = hex_bytes[i]
            u = unknown_bytes[i]
            diff = u ^ h  # XOR difference
            print(f"Position {i:2d}: Hex={h:02x} Unknown={u:02x} XOR_diff={diff:02x}")

    
    def hex_to_ascii(self, hex_string: str) -> str:
        """
        Convert hex to ASCII (JSON string).
        """
        try:
            # Convert hex to bytes then to ASCII
            bytes_data = bytes.fromhex(hex_string)
            ascii_str = bytes_data.decode('utf-8')
            
            # Validate it's proper JSON
            json.loads(ascii_str)
            return ascii_str
        except Exception as e:
            raise ValueError(f"Invalid hex to ASCII conversion: {str(e)}")

    def process_json_data(self, json_string: str) -> Dict[str, Any]:
        """
        Process JSON string into dictionary with validation.
        """
        if not validate_json(json_string):
            raise ValidationError("Invalid JSON string")
            
        return safe_json_loads(json_string)

    def hex_to_unknown(self, hex_string: str) -> str:
        """Convert hex to unknown format with header and transformed bytes."""
        try:
            # Process full hex string (don't skip header-length bytes)
            input_bytes = bytes.fromhex(hex_string)
            processed = bytearray()

            for i, byte in enumerate(input_bytes):
                # Split byte into two nibbles (4 bits each)
                high_nibble = (byte >> 4) & 0x0F
                low_nibble = byte & 0x0F

                # Transform each nibble into full bytes
                transformed_high = ((high_nibble ^ self.XOR_KEY) + i) % 256
                transformed_low = ((low_nibble ^ self.XOR_KEY) + i) % 256

                processed.append(transformed_high)
                processed.append(transformed_low)

            return self.HEADER + processed.hex()

        except Exception as e:
            if self._debug:
                print(f"❌ hex_to_unknown error: {str(e)}")
            return None

    def unknown_to_hex(self, unknown_string: str) -> str:
        """Convert unknown format back to original hex."""
        try:
            if not unknown_string.startswith(self.HEADER):
                return None

            data_part = unknown_string[len(self.HEADER):]
            input_bytes = bytes.fromhex(data_part)
            processed = bytearray()

            for i in range(0, len(input_bytes), 2):
                # Process byte pairs to reconstruct original byte
                high_byte = input_bytes[i]
                low_byte = input_bytes[i+1] if i+1 < len(input_bytes) else 0

                # Reverse transformations
                high_nibble = ((high_byte - i//2) ^ self.XOR_KEY) & 0x0F
                low_nibble = ((low_byte - i//2) ^ self.XOR_KEY) & 0x0F

                reconstructed = (high_nibble << 4) | low_nibble
                processed.append(reconstructed)

            return processed.hex()

        except Exception as e:
            if self._debug:
                print(f"❌ unknown_to_hex error: {str(e)}")
            return None

    def validate_conversion_pair(self, unknown_str, hex_str):
        """Validate conversion using the nibble transformation pattern."""
        if len(unknown_str) < len(self.HEADER):
            return False
            
        # Header validation
        if unknown_str[:len(self.HEADER)] != self.HEADER:
            return False

        unknown_data = unknown_str[len(self.HEADER):]
        hex_bytes = bytes.fromhex(hex_str)
        unknown_bytes = bytes.fromhex(unknown_data)

        # Validate length relationship: 2 unknown bytes per 1 hex byte
        if len(unknown_bytes) != 2 * len(hex_bytes):
            return False

        # Validate transformation pattern
        for i, hex_byte in enumerate(hex_bytes):
            high_nibble = (hex_byte >> 4) & 0x0F
            low_nibble = hex_byte & 0x0F
            
            expected_high = ((high_nibble ^ self.XOR_KEY) + i) % 256
            expected_low = ((low_nibble ^ self.XOR_KEY) + i) % 256

            if unknown_bytes[2*i] != expected_high:
                return False
            if (2*i + 1) < len(unknown_bytes) and unknown_bytes[2*i + 1] != expected_low:
                return False

        return True
