"Test cases for util.gpg module."

import unittest
import json

from hm_pyhelper.util.pgp import get_payload_from_clearsigned_message


SAMPLE_CLEARSIGNED_MESSAGE = """
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

{
  "key1": "value1",
  "key2": [1, 2, 3, 4]
}

-----BEGIN PGP SIGNATURE-----

iQGzBAEBCgAdFiEEfSH7Wj/J4hZxOpWqMy5fwG12lo0FAmIDUGEACgkQMy5fwG12
lo0WDwv+Nn8ffqY3oKOQv11eRkn+w4NcAp5XFqwYz0e5e+DEfjoYYTVAEgUdK1gF
W2u8Jed9rW710A6yYXHlIZWKSHsQ1sob5lK3R/r+/lFrXLYYwgFGBWJmph/wuiQW
OuZPpenOPNNjh37xxxxwxMj2kqUHKfJ489H2xOpPqpA4tWRKAspQCkv/AFVctcr5
1gWhJ5M5Mw/W6mgLswzonpsRy9M+vknuiDJ9F/Qe2hWUBJ0p7Si7YJkrynF3Oiqz
3D3JCiZAmoHq31hxO3bU7Sltf0lp1E7rG7mx7l0Pxq3fzNgaA9IW30NuF9J3YohK
Cv4pl11BYuUsBiQZktKcUwAsNj+UmZTnFBWACn4444+tFvs/tgG3wFZA33y3HAkl
6X9WGEa4d+DXeMgk2hr5oMRI9tZWqhNFqpu96CzrjJDxchgpeYjSCFiiX3po6Gyd
vH8uvB5hNKzj1vwqEtyyyyikUrPBe+273VeXNB+npF4LRok1MBjHZ49oZd2GZKBl
vo5u8szs
=i6qt
-----END PGP SIGNATURE-----
"""

SAMPLE_CLEARSIGNED_MESSAGE_NO_NEWLINE_AT_END = """
-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

{
  "key1": "value1",
  "key2": [1, 2, 3, 4]
}
-----BEGIN PGP SIGNATURE-----

iQGzBAEBCgAdFiEEfSH7Wj/J4hZxOpWqMy5fwG12lo0FAmIDUGEACgkQMy5fwG12
lo0WDwv+Nn8ffqY3oKOQv11eRkn+w4NcAp5XFqwYz0e5e+DEfjoYYTVAEgUdK1gF
W2u8Jed9rW710A6yYXHlIZWKSHsQ1sob5lK3R/r+/lFrXLYYwgFGBWJmph/wuiQW
OuZPpenOPNNjh37xxxxwxMj2kqUHKfJ489H2xOpPqpA4tWRKAspQCkv/AFVctcr5
1gWhJ5M5Mw/W6mgLswzonpsRy9M+vknuiDJ9F/Qe2hWUBJ0p7Si7YJkrynF3Oiqz
3D3JCiZAmoHq31hxO3bU7Sltf0lp1E7rG7mx7l0Pxq3fzNgaA9IW30NuF9J3YohK
Cv4pl11BYuUsBiQZktKcUwAsNj+UmZTnFBWACn4444+tFvs/tgG3wFZA33y3HAkl
6X9WGEa4d+DXeMgk2hr5oMRI9tZWqhNFqpu96CzrjJDxchgpeYjSCFiiX3po6Gyd
vH8uvB5hNKzj1vwqEtyyyyikUrPBe+273VeXNB+npF4LRok1MBjHZ49oZd2GZKBl
vo5u8szs
=i6qt
-----END PGP SIGNATURE-----
"""


class TestUtilPGP(unittest.TestCase):

    def test_empty_file(self):
        with self.assertRaises(RuntimeError) as exp:
            get_payload_from_clearsigned_message("")

        assert str(exp.exception) == \
            'Invalid message format, no --BEGIN PGP SIGNED MESSAGE-- header'

    def test_invalid_clearsigned_payload(self):
        with self.assertRaises(RuntimeError) as exp:
            get_payload_from_clearsigned_message("Just\nSome\nMessage\na\nb\nc")

        assert str(exp.exception) == \
            'Invalid message format, no --BEGIN PGP SIGNED MESSAGE-- header'

    def test_payload_extraction(self):
        payload = get_payload_from_clearsigned_message(SAMPLE_CLEARSIGNED_MESSAGE)
        d = json.loads(payload)
        assert d['key1'] == 'value1'
        assert d['key2'] == [1, 2, 3, 4]

        payload = get_payload_from_clearsigned_message(
            SAMPLE_CLEARSIGNED_MESSAGE_NO_NEWLINE_AT_END)
        d = json.loads(payload)
        assert d['key1'] == 'value1'
        assert d['key2'] == [1, 2, 3, 4]
