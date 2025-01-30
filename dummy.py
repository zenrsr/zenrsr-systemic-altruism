# dummy.py
from src.conversions import CryptoConverter
import json

converter = CryptoConverter(debug=True)

with open("data/data.json", "r") as f:
    test_cases = json.load(f)

def validate_conversion_pair(unknown_str, hex_str):
    # Validate header first
    if len(unknown_str) < 32:
        print("❌ Unknown string too short")
        return False
        
    header = unknown_str[:32]
    expected_header = converter.HEADER
    if header != expected_header:
        print("❌ Header mismatch")
        print(f"Expected: {expected_header}")
        print(f"Found:    {header}")
        return False

    # Extract data after header
    unknown_data = unknown_str[32:]
    
    try:
        hex_bytes = bytes.fromhex(hex_str)
        unknown_bytes = bytes.fromhex(unknown_data)
    except ValueError as e:
        print(f"❌ Invalid hex data: {str(e)}")
        return False

    # Strict length validation (2 unknown bytes per 1 hex byte)
    expected_unknown_length = 2 * len(hex_bytes)
    if len(unknown_bytes) != expected_unknown_length:
        print(f"❌ Length mismatch. Hex: {len(hex_bytes)} bytes, Unknown: {len(unknown_bytes)} bytes")
        print(f"Expected {expected_unknown_length} unknown bytes (2 per hex byte)")
        return False

    print("\n🔍 VALIDATING CONVERSION PAIR 🔍")
    
    for i in range(len(hex_bytes)):
        # Get corresponding pair of unknown bytes
        high_byte = unknown_bytes[2*i]
        low_byte = unknown_bytes[2*i + 1]
        
        # Reverse transformations
        high_nibble = ((high_byte - i) ^ converter.XOR_KEY) & 0x0F
        low_nibble = ((low_byte - i) ^ converter.XOR_KEY) & 0x0F
        
        # Reconstruct original byte
        reconstructed = (high_nibble << 4) | low_nibble
        original = hex_bytes[i]

        if reconstructed != original:
            print(f"\n🚨 Mismatch at position {i}:")
            print(f"Expected HEX:  0x{original:02x}")
            print(f"Reconstructed: 0x{reconstructed:02x}")
            print(f"Unknown Bytes: [0x{high_byte:02x}, 0x{low_byte:02x}]")
            print(f"After reversal: high=0x{high_nibble:01x}, low=0x{low_nibble:01x}")
            return False

    print("✅ Conversion Pair Valid")
    return True

# Process each test case
for case_id, case_data in test_cases.items():
    hex_value = case_data["hex"]
    unknown_value = case_data["unknown"]

    print(f"\n🚀 Test Case {case_id} - Hex Input:")
    print(hex_value)

    # Convert hex to unknown
    generated_unknown = converter.hex_to_unknown(hex_value)
    print("\n🟢 Generated Unknown String:")
    print(generated_unknown)

    # Convert back to hex
    reversed_hex = converter.unknown_to_hex(unknown_value)
    print("\n🔄 Reversed Hex String:")
    print(reversed_hex)

    # Validate forward conversion
    print("\n✅ Validating forward conversion:")
    forward_valid = validate_conversion_pair(unknown_value, hex_value)

    # Validate reverse conversion
    reverse_valid = False
    if forward_valid:
        print("\n✅ Validating reverse conversion:")
        reverse_valid = validate_conversion_pair(unknown_value, reversed_hex)

    # Final result
    if forward_valid and reverse_valid and hex_value == reversed_hex:
        print(f"\n✅ Test Case {case_id} Passed!")
    else:
        print(f"\n❌ Test Case {case_id} Failed!")