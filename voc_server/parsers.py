def tsv_rows(text):
    lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip() and not line.startswith("##")
    ]
    best = []
    for i, line in enumerate(lines):
        if "\t" not in line:
            continue
        headers = [x.strip() for x in line.split("\t")]
        rows = []
        for row in lines[i + 1 :]:
            if "\t" not in row:
                break
            cols = row.split("\t")
            if len(cols) < 2:
                break
            rows.append(
                {
                    header: cols[j].strip() if j < len(cols) else ""
                    for j, header in enumerate(headers)
                }
            )
        if len(rows) > len(best):
            best = rows
    return best


def parse_kpi_report(text):
    out = {"kpis": {}, "sections": [], "rows": tsv_rows(text)}
    for line in text.splitlines():
        cols = line.split("\t")
        if len(cols) >= 4 and cols[0] in {"customers", "inquiries", "cvr"}:
            out["kpis"][cols[0]] = {"npi": cols[1], "n1": cols[2], "lol": cols[3]}
        if line.startswith("## "):
            out["sections"].append(line[3:].strip())
    return out


def parse_intent_report(text):
    summary = {}
    for line in text.splitlines():
        cols = line.split("\t")
        if len(cols) == 2 and cols[0].startswith("total_"):
            summary[cols[0]] = cols[1]
    return {"summary": summary, "rows": tsv_rows(text)}


def parse_mix_report(text):
    return {
        "rows": tsv_rows(text),
        "sections": [
            line[3:].strip() for line in text.splitlines() if line.startswith("## ")
        ],
    }
