import ssl
import unittest
from urllib.parse import parse_qs

import server


class ServerP0Tests(unittest.TestCase):
    def test_date_filters_are_forwarded(self):
        query = parse_qs("date_from=2025-09-10&date_to=2025-09-12")
        args = server._common_filter_args(query)
        self.assertEqual(args["date_from"], "2025-09-10")
        self.assertEqual(args["date_to"], "2025-09-12")

    def test_multiple_fw_values_are_not_truncated(self):
        query = parse_qs("fw=FY25Q4W10,FY25Q4W11")
        args = server._common_filter_args(query)
        self.assertEqual(args["fw"], ["FY25Q4W10", "FY25Q4W11"])

    def test_single_fw_remains_backward_compatible(self):
        query = parse_qs("fw=FY25Q4W11")
        args = server._common_filter_args(query)
        self.assertEqual(args["fw"], "FY25Q4W11")

    def test_product_mix_uses_fw_array(self):
        query = parse_qs("fw=FY25Q4W11")
        args = server._common_filter_args(query, fw_mode="list")
        self.assertEqual(args["fw"], ["FY25Q4W11"])

    def test_tls_verification_is_enabled(self):
        self.assertNotEqual(server.SSL_CTX.verify_mode, ssl.CERT_NONE)
        self.assertTrue(server.SSL_CTX.check_hostname)

    def test_raw_query_disabled_by_default(self):
        if not server.ALLOW_RAW_QUERY:
            self.assertNotIn("query_voc", server.PUBLIC_MCP_TOOLS)


if __name__ == "__main__":
    unittest.main()
