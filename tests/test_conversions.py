# tests/test_conversion.py

import json
import pytest
from src.conversions import CryptoConverter

@pytest.fixture
def converter():
    return CryptoConverter()

@pytest.fixture
def test_data():
    return {
        "hex": "7b2275726c223a2268747470733a2f2f6173736574732d676c6f62616c2e776562736974652d66696c65732e636f6d2f3633386165633530623961323363656331376238633464312f3633663966613663623962623130333538396630383530615f7a713768337335316a6166636e6c6474646677632e6a7067222c2268617368223a223037373766666637383338313031303038303363336330306665666566306664222c2273656172636848617368223a223234313233306a6871797767736f656534686a67656462306461633038222c226c6566745f657965223a5b3235352c3134325d2c2272696768745f657965223a5b3331372c3134375d2c226e6f7365223a5b3238302c3138325d2c226c6566745f6d6f757468223a5b3234382c3230325d2c2272696768745f6d6f757468223a5b3331392c3230395d2c2265787069726554696d65223a313733353633373234303835312c22616254657374223a6e756c6c2c22706f726e223a66616c73657d",
        "unknown": "d8ab19d5c7a0f27c10fa57540506ac683bdf3c86c31f402beaf7e441d7eb789364cce03fac2f7ba75b0c4696dc30e8f20bca09ed71c3e5fc70980ac1581c059c9c17cc118f6187c4a20c1f8b0e83b410e3f6fa6d50d48e006be371843453f675e7233888b4150c5f1c26bf049aad1b6c0fa97a225baf1fec3cf31356897ef37be650aacdd25ff78dfc304e73d779768e6b19efe5af9477e074e3de07fcaec66014dea40fe186af33fa519d816ead854c6da927eb7dd8c349d14bbf68f4a97623ed755cfdc3cf09ab925af7f248f7d946a80ef46ae91094bf675dde11e5a8ba75d3cf98a63e9acea0e1dadf78c6e839b0ca4c44bfd13c80155d82d14613c68b9843074f02d74710a485a0ae2914746de6583b9cae685aa66239d3f2cefb657033269d55aa3c4dc6a6c715cc7e4aa5ed6431d486bd6a3b12fe9dcac4635f98232f5c31e16e41daceccb6e584a62b9dee756e29c2adf82def9650fad0b0aaf9bebf278dd97861d278e621043cb4d6858912f2ebb697ead4f9956100a5887f1feb84"
    }

def test_hex_to_ascii(converter, test_data):
    result = converter.hex_to_ascii(test_data['hex'])
    assert isinstance(result, str)
    assert json.loads(result) is not None

def test_hex_to_unknown(converter, test_data):
    result = converter.hex_to_unknown(test_data['hex'])
    assert isinstance(result, str)
    assert '.' in result

def test_unknown_to_hex(converter, test_data):
    result = converter.unknown_to_hex(test_data['unknown'])
    assert isinstance(result, str)
    assert len(result) % 2 == 0  # Hex string should have even length

def test_validation_pair(converter, test_data):
    result = converter.validate_conversion_pair(
        test_data['hex'],
        test_data['unknown']
    )
    assert isinstance(result, bool)

def test_invalid_hex():
    converter = CryptoConverter()
    with pytest.raises(ValueError):
        converter.hex_to_ascii("invalid hex")

def test_invalid_unknown():
    converter = CryptoConverter()
    with pytest.raises(ValueError):
        converter.unknown_to_hex("invalid unknown")

if __name__ == "__main__":
    pytest.main([__file__])
