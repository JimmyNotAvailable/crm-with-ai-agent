# product_parser.py
"""
Utility functions to parse product body markdown for vectorization
"""
import re


def parse_body_md(body_md: str) -> str:
    """
    Parse product body markdown and clean it for embedding
    
    Args:
        body_md: Raw markdown body from product data
        
    Returns:
        Cleaned text suitable for embedding
    """
    if not body_md:
        return ""

    text = body_md

    # remove markdown
    text = re.sub(r"#", "", text)
    text = re.sub(r"\*\*", "", text)
    text = re.sub(r"\*", "", text)

    # normalize
    text = re.sub(r"-\s*", "", text)
    text = re.sub(r"\n{2,}", "\n", text)
    text = re.sub(r"\s+", " ", text)

    # semantic labels
    text = text.replace("CPU", "CPU:")
    text = text.replace("Ram", "RAM:")
    text = text.replace("Ổ cứng", "Storage:")
    text = text.replace("Card đồ họa", "GPU:")
    text = text.replace("Màn hình", "Display:")
    text = text.replace("Pin", "Battery:")
    text = text.replace("Hệ điều hành", "OS:")
    text = text.replace("Giá bán", "Price:")

    return text.strip()


def product_to_text(product: dict) -> str:
    """
    Convert product dict to text for vectorization
    
    Args:
        product: Product dictionary with title, _meta, body_md
        
    Returns:
        Text representation of product
    """
    parsed_body = parse_body_md(product.get("body_md", ""))

    return f"""
Sản phẩm: {product.get("title")}
Thương hiệu: {product.get("_meta", {}).get("brand")}
Danh mục: {product.get("_meta", {}).get("category")}
Giá bán: {product.get("_meta", {}).get("price")} VND

Thông tin kỹ thuật:
{parsed_body}
""".strip()
