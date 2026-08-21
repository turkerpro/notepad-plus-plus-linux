"""
Encoding and Line Ending detection and conversion for Notepad++ Linux.
"""
from typing import Tuple
import chardet

# Common encodings supported in Notepad++
ENCODINGS = [
    ("UTF-8", "utf-8"),
    ("UTF-8 with BOM", "utf-8-sig"),
    ("UTF-16 LE", "utf-16-le"),
    ("UTF-16 BE", "utf-16-be"),
    ("ANSI / Windows-1252", "cp1252"),
    ("Turkish (Windows-1254)", "cp1254"),
    ("Turkish (ISO-8859-9)", "iso-8859-9"),
    ("Western (ISO-8859-1)", "iso-8859-1"),
    ("Central European (Windows-1250)", "cp1250"),
    ("Cyrillic (Windows-1251)", "cp1251"),
    ("Greek (Windows-1253)", "cp1253"),
    ("Arabic (Windows-1256)", "cp1256"),
    ("Baltic (Windows-1257)", "cp1257"),
    ("Chinese Simplified (GB2312)", "gb2312"),
    ("Chinese Traditional (Big5)", "big5"),
    ("Japanese (Shift_JIS)", "shift_jis"),
    ("Korean (EUC-KR)", "euc-kr"),
    ("ASCII", "ascii"),
]

EOL_WINDOWS = "CRLF"
EOL_UNIX = "LF"
EOL_MAC = "CR"

EOL_CHARS = {
    EOL_WINDOWS: "\r\n",
    EOL_UNIX: "\n",
    EOL_MAC: "\r"
}


def detect_line_ending(text: str) -> str:
    """Detect predominant line ending in text."""
    crlf_count = text.count("\r\n")
    # Replace CRLF temporarily to count lone \r and \n
    text_no_crlf = text.replace("\r\n", "")
    lf_count = text_no_crlf.count("\n")
    cr_count = text_no_crlf.count("\r")

    if crlf_count >= lf_count and crlf_count >= cr_count and crlf_count > 0:
        return EOL_WINDOWS
    if cr_count > lf_count and cr_count > 0:
        return EOL_MAC
    return EOL_UNIX


def convert_line_endings(text: str, target_eol: str) -> str:
    """Normalize text line endings to target format."""
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    if target_eol == EOL_WINDOWS:
        return normalized.replace("\n", "\r\n")
    elif target_eol == EOL_MAC:
        return normalized.replace("\n", "\r")
    return normalized


def read_file_with_encoding(file_path: str) -> Tuple[str, str, str]:
    """
    Read file from disk, detecting encoding and EOL.
    Returns (content, encoding_name, eol_type).
    """
    with open(file_path, "rb") as f:
        raw_bytes = f.read()

    # Check UTF-8 BOM
    if raw_bytes.startswith(b"\xef\xbb\xbf"):
        try:
            content = raw_bytes.decode("utf-8-sig")
            eol = detect_line_ending(content)
            return content, "UTF-8 with BOM", eol
        except UnicodeDecodeError:
            pass

    # Check UTF-16 LE BOM
    if raw_bytes.startswith(b"\xff\xfe"):
        try:
            content = raw_bytes.decode("utf-16")
            eol = detect_line_ending(content)
            return content, "UTF-16 LE", eol
        except UnicodeDecodeError:
            pass

    # Check UTF-16 BE BOM
    if raw_bytes.startswith(b"\xfe\xff"):
        try:
            content = raw_bytes.decode("utf-16-be")
            eol = detect_line_ending(content)
            return content, "UTF-16 BE", eol
        except UnicodeDecodeError:
            pass

    # Try standard UTF-8 first
    try:
        content = raw_bytes.decode("utf-8")
        eol = detect_line_ending(content)
        return content, "UTF-8", eol
    except UnicodeDecodeError:
        pass

    # Try chardet detection
    detected = chardet.detect(raw_bytes)
    detected_encoding = detected.get("encoding") or "cp1254"

    # Map detected encoding to friendly name
    try:
        content = raw_bytes.decode(detected_encoding)
        eol = detect_line_ending(content)
        # Find friendly name
        for friendly_name, enc_code in ENCODINGS:
            if enc_code.lower() == detected_encoding.lower():
                return content, friendly_name, eol
        return content, detected_encoding.upper(), eol
    except Exception:
        content = raw_bytes.decode("cp1254", errors="replace")
        eol = detect_line_ending(content)
        return content, "Turkish (Windows-1254)", eol


def save_file_with_encoding(file_path: str, content: str, encoding_name: str, eol_type: str) -> None:
    """Save text content to disk using the specified encoding and EOL."""
    content_with_eol = convert_line_endings(content, eol_type)

    target_encoding = "utf-8"
    for friendly_name, enc_code in ENCODINGS:
        if friendly_name == encoding_name:
            target_encoding = enc_code
            break

    with open(file_path, "w", encoding=target_encoding, errors="replace", newline="") as f:
        f.write(content_with_eol)
