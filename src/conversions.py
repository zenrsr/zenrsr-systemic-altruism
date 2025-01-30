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
        try:
            result = self.HEADER
            input_bytes = bytes.fromhex(hex_string)
            processed = bytearray()
            
            # print("\n--- HEX → UNKNOWN DEBUG ---")
            for i, byte in enumerate(input_bytes):  # Print only first 16 bytes
                transformed = byte ^ 0xD8
                transformed = (transformed + (i % 256)) & 0xFF

                # print(f"Pos {i}: HEX={byte:02x} → XOR={byte^0xD8:02x} → OFFSET={transformed:02x}")

                processed.append(transformed)

            return result + processed.hex()
        except Exception as e:
            return None


    def unknown_to_hex(self, unknown_string: str) -> str:
        try:
            if not unknown_string.startswith(self.HEADER):
                return None

            input_bytes = bytes.fromhex(unknown_string[len(self.HEADER):])
            processed = bytearray()

            # print("\n--- UNKNOWN → HEX DEBUG ---")
            for i, byte in enumerate(input_bytes):  # Print only first 16 bytes
                reversed_offset = (byte - (i % 256)) & 0xFF
                transformed = reversed_offset ^ 0xD8

                # print(f"Pos {i}: UNKNOWN={byte:02x} → REVERSED_OFFSET={reversed_offset:02x} → XOR_BACK={transformed:02x}")

                processed.append(transformed)

            return processed.hex()

        except Exception as e:
            print(f"Error in unknown_to_hex: {str(e)}")
            return None



    def validate_conversion_pair(self, unknown_str, hex_str):
        if len(unknown_str) < 32:
            return False

        unknown_data = unknown_str[32:]  # Remove header
        if len(unknown_data) != len(hex_str):
            print("Mismatch in length after header removal")
            return False

        unknown_bytes = bytes.fromhex(unknown_data)
        hex_bytes = bytes.fromhex(hex_str)

        print("Unknown Data (After Header):", unknown_bytes.hex())
        print("Hex Data (Original):", hex_bytes.hex())

        for i in range(len(unknown_bytes)):
            transformed = (unknown_bytes[i] - (i % 16)) & 0xFF
            transformed = transformed ^ 0xD8  # Undo XOR with 0xD8
            
            print(f"Pos {i:3}: Unknown={unknown_bytes[i]:02x} -> Transformed={transformed:02x} | Expected={hex_bytes[i]:02x}")

            if transformed != hex_bytes[i]:
                return False

        return True
