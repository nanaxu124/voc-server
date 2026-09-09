with open('server.py', 'r') as f:
    lines = f.readlines()

out = []
skip = False
for line in lines:
    if 'elif self.path.startswith("/api/mcp/mix_data"):' in line:
        skip = True
        out.append(line)
        out.append("""            try:
                from urllib.parse import urlparse, parse_qs
                query = parse_qs(urlparse(self.path).query)
                args = {"product_type": "iPhone"}
                if "date_from" in query and query["date_from"][0]:
                    args["date_from"] = query["date_from"][0]
                if "date_to" in query and query["date_to"][0]:
                    args["date_to"] = query["date_to"][0]
                if "fw" in query and query["fw"][0]:
                    args["fw"] = [fw.strip() for fw in query["fw"][0].split(",")]
                if "npi_sublobs" in query and query["npi_sublobs"][0]:
                    args["npi_sublobs"] = [x.strip() for x in query["npi_sublobs"][0].split(",")]
                if "n1_sublobs" in query and query["n1_sublobs"][0]:
                    args["n1_sublobs"] = [x.strip() for x in query["n1_sublobs"][0].split(",")]

                res = call_voc_mcp("voc_npi_product_mix", args)
                if "error" in res:
                    self._send_error(500, res["error"])
                    return
                
                text = res.get("raw_text", "")
                parsed_data = parse_mix_text(text)
                self._send_json({"success": True, "source": "voc_npi_product_mix", "data": parsed_data})
            except Exception as e:
                self._send_error(500, str(e))
            return
""")
    elif skip and 'elif self.path.startswith("/api/mcp/product_issues"):' in line:
        skip = False
        out.append(line)
    elif not skip:
        out.append(line)

with open('server.py', 'w') as f:
    f.writelines(out)
