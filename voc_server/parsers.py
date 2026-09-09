import re


def _to_int(value, default=0):
    try:
        return int(str(value).replace(",", "").strip())
    except Exception:
        return default


def _to_float(value, default=0.0):
    try:
        return float(str(value).replace("%", "").replace("pt", "").strip())
    except Exception:
        return default


def _questions(value):
    out = []
    for raw in (value or "").split("; "):
        raw = raw.strip()
        if not raw:
            continue
        match = re.match(r"^(.*?)\((\d+)\)$", raw)
        out.append({"name": match.group(1) if match else raw, "count": _to_int(match.group(2)) if match else 0})
    return out


def tsv_rows(text):
    lines = [line.rstrip() for line in text.splitlines() if line.strip() and not line.startswith("##")]
    best = []
    for i, line in enumerate(lines):
        if "\t" not in line:
            continue
        headers = [x.strip() for x in line.split("\t")]
        rows = []
        for row in lines[i + 1:]:
            if "\t" not in row:
                break
            cols = row.split("\t")
            if len(cols) < 2:
                break
            rows.append({h: cols[j].strip() if j < len(cols) else "" for j, h in enumerate(headers)})
        if len(rows) > len(best):
            best = rows
    return best


def parse_kpi_report(text):
    data = {"kpis": {}, "program": [], "feature": [], "trend": [], "date_timestamp": None}
    section = "kpi"
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("## "):
            title = line[3:]
            section = "program" if "Program" in title else "feature" if "Feature" in title else "trend" if ("每日趋势" in title or "趋势" in title) else "kpi"
            continue
        cols = line.split("\t")
        if section == "kpi" and len(cols) >= 4 and cols[0] in {"customers", "inquiries", "cvr"}:
            data["kpis"][cols[0]] = {"npi": cols[1], "n1": cols[2], "lol": cols[3]}
        elif section in {"program", "feature"} and len(cols) >= 4 and cols[0] != "name":
            data[section].append({
                "name": cols[0], "inquiries": _to_int(cols[1]), "inquiryPct": _to_float(cols[2]), "cvr": _to_float(cols[3]),
                "sessionCount": 0, "sessionOrderCount": 0, "sampledQ": _questions(cols[4] if len(cols) > 4 else "")
            })
        elif section == "trend" and len(cols) >= 3 and cols[0] != "date" and not cols[0].startswith("duration"):
            data["trend"].append({"date": cols[0], "npi": _to_int(cols[1]), "n1": _to_int(cols[2])})
    if data["trend"]:
        data["date_timestamp"] = str(data["trend"][-1]["date"]).replace("-", "/")
    return data


def parse_intent_report(text):
    summary = {}
    rows = []
    header = None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        if line.startswith("total_") or line.startswith("cvr_avg"):
            cols = line.split("\t")
            if len(cols) >= 2:
                summary[cols[0]] = cols[1]
            continue
        if line.startswith("inquiry\t") or line.startswith("first_intent\t"):
            header = line.split("\t")
            continue
        if not header or "\t" not in line:
            continue
        cols = line.split("\t")
        if len(cols) < 7:
            continue
        qlist = [{"inquiryName": q["name"], "inquiryCount": q["count"]} for q in _questions(cols[7] if len(cols) > 7 else "")]
        if "customer_count" in header:
            sessions, inquiries, cvr = _to_int(cols[4]), _to_int(cols[5]), _to_float(cols[6])
        else:
            inquiries, sessions, cvr = _to_int(cols[4]), _to_int(cols[4]), _to_float(cols[6])
        rows.append({
            "firstIntention": cols[0], "twoIntention": cols[1], "threeIntention": cols[2], "fourIntention": cols[3],
            "inquiries": inquiries, "sessionCount": sessions, "sessionOrderCount": int(round(sessions * cvr / 100.0)), "inquirieList": qlist
        })
    return [{
        "type": "iPhone", "prodName": "iPhone 17", "date": "2025-09-12", "summary": summary,
        "intentDetailList": [{"fy": "FY25", "fq": "Q4", "fw": "W11", "intentList": rows}]
    }]


def parse_mix_report(text):
    npi = {"grandTotal": 0, "seriesData": {}}
    n1 = {"grandTotal": 0, "seriesData": {}}
    storage = {"npiOverviewTotal": 0, "n1OverviewTotal": 0, "npiStorageTotal": 0, "n1StorageTotal": 0, "npiStorage": {}, "n1Storage": {}}
    color = {"npiOverviewTotal": 0, "n1OverviewTotal": 0, "npiColorTotal": 0, "n1ColorTotal": 0, "npiColor": {}, "n1Color": {}}
    for sec in text.split("## "):
        lines = [x.strip() for x in sec.splitlines() if x.strip()]
        if not lines:
            continue
        title = lines[0]
        if title.startswith("NPI Product Mix") or title.startswith("N-1 Product Mix"):
            target = npi if title.startswith("NPI Product Mix") else n1
            for line in lines[1:]:
                if line.startswith("period="):
                    match = re.search(r"total_customers=(\d+)", line)
                    if match:
                        target["grandTotal"] = _to_int(match.group(1))
                elif "\t" in line and not line.startswith("series\t"):
                    cols = line.split("\t")
                    if len(cols) < 3 or cols[0] == "TOTAL iPhone":
                        continue
                    series, sublob, count = cols[0], cols[1], _to_int(cols[2])
                    target["seriesData"].setdefault(series, {"total": 0, "subLobs": {}})
                    if sublob == "小计": target["seriesData"][series]["total"] = count
                    elif sublob: target["seriesData"][series]["subLobs"][sublob] = count
        elif title.startswith("Storage Mix") or title.startswith("Color Mix"):
            is_storage = title.startswith("Storage Mix")
            target = storage if is_storage else color
            npi_key, n1_key = ("npiStorage", "n1Storage") if is_storage else ("npiColor", "n1Color")
            for line in lines[1:]:
                if line.startswith("分母(customers)"):
                    den = re.search(r"NPI=(\d+)\s+N-1=(\d+)", line)
                    qty = re.search(r"分子合计\(quantity\)\s*NPI=(\d+)\s*N-1=(\d+)", line)
                    if den:
                        target["npiOverviewTotal"], target["n1OverviewTotal"] = _to_int(den.group(1)), _to_int(den.group(2))
                    if qty:
                        target["npiStorageTotal" if is_storage else "npiColorTotal"] = _to_int(qty.group(1))
                        target["n1StorageTotal" if is_storage else "n1ColorTotal"] = _to_int(qty.group(2))
                elif "\t" in line and not line.startswith("storage\t") and not line.startswith("color\t"):
                    cols = line.split("\t")
                    if len(cols) >= 5:
                        if _to_int(cols[1]) > 0: target[npi_key][cols[0]] = _to_int(cols[1])
                        if _to_int(cols[3]) > 0: target[n1_key][cols[0]] = _to_int(cols[3])
    return {"npi_product_mix": npi, "n1_product_mix": n1, "part4": {"storage": storage, "color": color}}


def parse_price_report(text):
    summary, daily, mode = {}, [], None
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        upper = line.upper()
        if "SUMMARY" in upper:
            mode = "summary"; continue
        if "BREAKDOWN" in upper or line.startswith("date\t"):
            mode = "daily"; continue
        cols = line.split("\t")
        if mode == "summary" and len(cols) >= 4:
            if cols[0] == "NPI":
                summary.update(price_related=_to_int(cols[1]), customers=_to_int(cols[2]), avg_ratio_pct=_to_float(cols[3]))
            elif cols[0] in {"N-1", "N1"}:
                summary.update(n1_price_related=_to_int(cols[1]), n1_customers=_to_int(cols[2]), n1_avg_ratio_pct=_to_float(cols[3]))
        elif mode == "daily" and len(cols) >= 4 and re.match(r"^\d{4}-\d{2}-\d{2}$", cols[0]):
            daily.append({"date": cols[0], "npi_ratio_pct": _to_float(cols[2]), "n1_ratio_pct": _to_float(cols[3]), "stack_total_pct": _to_float(cols[4]) if len(cols) > 4 else 0.0})
    return {"summary": summary, "daily": daily}
