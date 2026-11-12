def mask_imei(imei):
    """
    Mask an IMEI, keeping only its last four digits visible.

    Hyphens and spaces are ignored. Invalid values return "Invalid IMEI"
    instead of raising an exception.
    """
    if not isinstance(imei, str):
        return "Invalid IMEI"

    cleaned = imei.replace("-", "").replace(" ", "")

    if not cleaned.isdigit() or len(cleaned) <= 4:
        return "Invalid IMEI"

    return "*" * (len(cleaned) - 4) + cleaned[-4:]


def parse_parts_order(text):
    """
    Parse entries such as 'screen x1; battery x2' into a dictionary.

    Invalid entries are skipped. A valid entry has a non-empty part name,
    an 'x' separator, and a positive integer quantity.
    """
    if not isinstance(text, str):
        return {}

    order = {}

    for item in text.split(";"):
        item = item.strip()
        if not item or "x" not in item:
            continue

        part, qty_text = item.rsplit("x", 1)
        part = part.strip()
        qty_text = qty_text.strip()

        if not part:
            continue

        try:
            quantity = int(qty_text)
        except (TypeError, ValueError):
            continue

        if quantity <= 0:
            continue

        order[part] = quantity

    return order


def parse_model(text):
    """
    Split a phone description into (brand, model).

    Invalid or incomplete input returns two empty strings.
    """
    if not isinstance(text, str):
        return "", ""

    parts = text.strip().split(None, 1)

    if len(parts) != 2 or not parts[0] or not parts[1].strip():
        return "", ""

    brand, model = parts
    return brand.title(), model.strip()


def main():
    print("==== Running mask_imei ====")
    value = input("Enter an IMEI number (e.g. 35-209900-176148-1): ")
    print("Masked IMEI:", mask_imei(value))

    print("\n==== Running parse_parts_order ====")
    value = input(
        "Enter parts and quantities as PART xQTY separated by ; "
        "(e.g. screen x1; battery x2): "
    )
    print("Parts order:", parse_parts_order(value))

    print("\n==== Running parse_model ====")
    value = input("Enter the phone brand and model (e.g. Samsung Galaxy S23): ")
    print("Brand and model:", parse_model(value))


if __name__ == "__main__":
    main()
