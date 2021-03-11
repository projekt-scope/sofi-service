import json
import unittest

import requests


class TestSofi(unittest.TestCase):

    files = {
        "dat_file": ("example_frame.dat", open("dat/example_frame.dat", "r")),
    }

    def test_sofi_send_file(self):
        print(self.files)
        response = requests.post(
            "http://172.20.10.102:8001/dat2result/frame", files=self.files,
        )
        response_dict = json.loads(response.text)
        self.assertEqual(
            type(response_dict) == dict, True, "Not the right return format"
        )
        self.assertEqual(response.status_code, 200, "Service is not working")


if __name__ == "__main__":
    unittest.main()
