"""Fixed Stage 2 vector for cross-language signing interoperability."""

TEST_BODY = b'{"sku":"SKU-1","stock":5}'
TEST_SECRET = b"stage-2-test-secret"
EXPECTED_BODY_SHA256 = "541dffad76efde94986c635a29f19b29df65fc7d07b44da2576ce9fec007a802"
EXPECTED_CANONICAL_REQUEST = (
    "POST\n"
    "/api/catalog/products?page=2&tag=blue%20sky&tag=sale\n"
    "1787390042\n"
    "7e488fb0-a1c8-4eca-9d7e-b82d7486f4c3\n"
    "541dffad76efde94986c635a29f19b29df65fc7d07b44da2576ce9fec007a802"
)
EXPECTED_SIGNATURE = "2c1d0ec86ff34e7d057d2004df2ff4e88745b393938984d956658d748f5f104a"
