# Initialize converter with debug mode ON
from src.conversions import CryptoConverter

converter = CryptoConverter(debug=True)

# Test Case from crypto.json (Index 0)
hex_value = "7b2275726c223a2268747470733a2f2f6173736574732d676c6f62616c2e776562736974652d66696c65732e636f6d2f3633386165633530623961323363656331376238633464312f3633663966613663623962623130333538396630383530615f7a713768337335316a6166636e6c6474646677632e6a7067222c2268617368223a223037373766666637383338313031303038303363336330306665666566306664222c2273656172636848617368223a223234313233306a6871797767736f656534686a67656462306461633038222c226c6566745f657965223a5b3235352c3134325d2c2272696768745f657965223a5b3331372c3134375d2c226e6f7365223a5b3238302c3138325d2c226c6566745f6d6f757468223a5b3234382c3230325d2c2272696768745f6d6f757468223a5b3331392c3230395d2c2265787069726554696d65223a313733353633373234303835312c22616254657374223a6e756c6c2c22706f726e223a66616c73657d"

# Convert to "unknown" format
unknown_value = converter.hex_to_unknown(hex_value)
print("\nGenerated Unknown String:")
print(unknown_value)

# Convert back to hex
reversed_hex = converter.unknown_to_hex(unknown_value)
print("\nReversed Hex String:")
print(reversed_hex)

def validate_conversion_pair(unknown_str, hex_str):
    if len(unknown_str) < 32:
        return False

    unknown_data = unknown_str[32:]  # Remove header
    if len(unknown_data) != len(hex_str):
        print(f"❌ Mismatch in length: Unknown={len(unknown_data)}, Hex={len(hex_str)}")
        return False

    unknown_bytes = bytes.fromhex(unknown_data)
    hex_bytes = bytes.fromhex(hex_str)

    print("\n--- VALIDATING CONVERSION PAIR ---")
    for i in range(len(unknown_bytes)):
        transformed = (unknown_bytes[i] - (i % 16)) & 0xFF
        transformed = transformed ^ 0xD8

        if transformed != hex_bytes[i]:
            print(f"❌ Mismatch at Pos {i}: Unknown={unknown_bytes[i]:02x} → Transformed={transformed:02x} (Expected={hex_bytes[i]:02x})")
            return False  # Immediately fail on mismatch

    print("✅ Conversion Pair Valid")
    return True

# Validate the forward conversion
print("\nValidating forward conversion:")
forward_valid = validate_conversion_pair(unknown_value, hex_value)

# Validate the reverse conversion
print("\nValidating reverse conversion:")
reverse_valid = validate_conversion_pair(unknown_value, reversed_hex)

# Check if both validations and the round-trip conversion are correct
if forward_valid and reverse_valid and hex_value == reversed_hex:
    print("\n✅ All Tests Passed!")
    print("- Forward conversion validated")
    print("- Reverse conversion validated")
    print("- Hex values match")
else:
    print("\n❌ Tests Failed!")
    if not forward_valid:
        print("- Forward conversion validation failed")
    if not reverse_valid:
        print("- Reverse conversion validation failed")
    if hex_value != reversed_hex:
        print("- Hex value mismatch:")
        print(f"Original Hex: {hex_value}")
        print(f"Reversed Hex: {reversed_hex}")