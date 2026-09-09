def query_first(query, key):
    values = query.get(key) or []
    value = values[0].strip() if values and values[0] else ""
    return value or None


def query_csv(query, key):
    value = query_first(query, key)
    return [x.strip() for x in value.split(",") if x.strip()] if value else []


def common_filter_args(query, *, fw_mode="auto"):
    args = {"product_type": "iPhone"}
    for key in ("date_from", "date_to"):
        value = query_first(query, key)
        if value:
            args[key] = value
    fws = query_csv(query, "fw")
    if fws:
        args["fw"] = fws if fw_mode == "list" or len(fws) > 1 else fws[0]
    return args
