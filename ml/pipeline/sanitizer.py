import re
from typing import Set

CPP_KEYWORDS_AND_TYPES: Set[str] = {
    "int", "double", "float", "char", "bool", "void", "return", "const", "auto",
    "class", "struct", "enum", "union", "if", "else", "while", "for", "do",
    "switch", "case", "default", "break", "continue", "static_cast", "dynamic_cast",
    "reinterpret_cast", "const_cast", "namespace", "using", "include", "new",
    "delete", "nullptr", "true", "false", "unsigned", "signed", "short", "long",
    "operator", "sizeof", "typedef", "template", "typename", "public", "private",
    "protected", "virtual", "friend", "inline", "constexpr", "static", "volatile",
    "this", "throw", "try", "catch", "explicit", "export", "extern", "typeid",
    # Common Standard Library types & symbols
    "std", "cout", "cin", "cerr", "endl", "string", "vector", "map", "set",
    "pair", "queue", "stack", "list", "deque", "array", "tuple", "iterator",
    "size_t", "ptrdiff_t", "main", "main()", "iostream", "iomanip", "cmath",
    "cctype", "algorithm", "setprecision", "fixed", "left", "right"
}

PATH_PATTERN = re.compile(r"(?:[a-zA-Z]:[\\/]|/workspace/|/tmp/)[^\s:]+\.cpp", re.IGNORECASE)
QUOTED_ENTITY_PATTERN = re.compile(r"'([^']+)'")
BACKTICK_ENTITY_PATTERN = re.compile(r"`([^']+)'")
PUNCTUATION_PATTERN = re.compile(r"^[^a-zA-Z0-9_]+$")


def sanitize_diagnostic_message(raw_msg: str) -> str:
    """
    Sanitizes compiler diagnostic messages:
    1. Removes any host file paths.
    2. Replaces user-invented identifiers with '<ID>', preserving C++ keywords,
       standard library types, symbols, and standard diagnostic terms.
    3. Normalizes whitespace and quotes.
    """
    if not raw_msg:
        return ""

    msg = raw_msg.strip()

    # 1. Remove file paths
    msg = PATH_PATTERN.sub("<FILE>", msg)

    # 2. Sanitize single-quoted tokens ('foo' -> '<ID>')
    def replace_quoted(match: re.Match) -> str:
        token = match.group(1).strip()
        # Single symbols/delimiters like ';', '}', ')'
        if PUNCTUATION_PATTERN.match(token):
            return f"'{token}'"

        # Standard namespace types
        if token.startswith("std::"):
            return f"'{token}'"

        # Multi-part types like 'const char*' or 'long long'
        parts = [p.strip("&*") for p in token.split()]
        if parts and all(
            p.lower() in CPP_KEYWORDS_AND_TYPES or p.startswith("std::") or bool(PUNCTUATION_PATTERN.match(p))
            for p in parts if p
        ):
            return f"'{token}'"

        return "'<ID>'"

    msg = QUOTED_ENTITY_PATTERN.sub(replace_quoted, msg)

    # 3. Sanitize backtick linker errors (`foo()' -> `<ID>()')
    def replace_backtick(match: re.Match) -> str:
        token = match.group(1).strip()
        fn_name = token.split("(")[0].strip()
        if fn_name in CPP_KEYWORDS_AND_TYPES or fn_name.startswith("std::"):
            return f"`{token}'"
        return "`<ID>()'"

    msg = BACKTICK_ENTITY_PATTERN.sub(replace_backtick, msg)

    return msg


def sanitize_notes_and_hints(notes: list) -> list:
    return [sanitize_diagnostic_message(n) for n in notes]
