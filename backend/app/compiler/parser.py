import re
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any

@dataclass
class DiagnosticNote:
    line: Optional[int]
    column: Optional[int]
    message: str

@dataclass
class ParsedDiagnostic:
    line: Optional[int]
    column: Optional[int]
    severity: str  # "error", "warning", "fatal error"
    message: str
    notes: List[str] = field(default_factory=list)
    is_primary: bool = False
    is_follow_on: bool = False

# Regex matching standard GCC diagnostic lines:
# Examples:
# /workspace/main.cpp:4:3: error: expected ';' before 'return'
# /workspace/main.cpp:10: error: 'foo' was not declared in this scope
# /workspace/main.cpp:5:10: fatal error: non_existent.h: No such file or directory
# /workspace/main.cpp:8:5: note: 'std::cout' is defined in header '<iostream>'
DIAG_PATTERN = re.compile(
    r"^(?:/workspace/)?(?:[^\n:]+):(\d+):(?:(\d+):)?\s*(fatal error|error|warning|note):\s*(.+)$",
    re.IGNORECASE
)

# Regex matching GCC linker errors:
# Examples:
# /workspace/main.cpp:4: undefined reference to 'foo()'
# /tmp/ccXX.o: in function 'main': /workspace/main.cpp:4: undefined reference to 'bar()'
LINKER_PATTERN = re.compile(
    r"(?:/workspace/)?(?:[^\n:]+):(\d+):(?:\([^\)]+\):)?\s*(undefined reference to .+)$",
    re.IGNORECASE
)

# Alternative linker error with no line number:
LINKER_NO_LINE_PATTERN = re.compile(
    r"(?:undefined reference to `?([^']+)'?|undefined reference to (.+))",
    re.IGNORECASE
)

def parse_compiler_output(raw_output: str) -> List[ParsedDiagnostic]:
    """
    Parses g++ stdout/stderr output into a list of structured diagnostic records,
    attaching notes to their parent errors and computing primary vs. follow-on flags.
    """
    if not raw_output or not raw_output.strip():
        return []

    lines = raw_output.strip().splitlines()
    diagnostics: List[ParsedDiagnostic] = []
    current_diag: Optional[ParsedDiagnostic] = None

    for raw_line in lines:
        line_str = raw_line.strip()
        if not line_str:
            continue

        # Check standard diagnostic format
        match = DIAG_PATTERN.match(line_str)
        if match:
            line_num = int(match.group(1))
            col_num = int(match.group(2)) if match.group(2) else None
            severity = match.group(3).lower()
            msg = match.group(4).strip()

            if severity == "note":
                # Attach note to previous error if exists
                if current_diag:
                    current_diag.notes.append(msg)
                else:
                    # Note without preceding error (rare), keep as info
                    diag = ParsedDiagnostic(
                        line=line_num,
                        column=col_num,
                        severity="note",
                        message=msg
                    )
                    diagnostics.append(diag)
                    current_diag = diag
            else:
                diag = ParsedDiagnostic(
                    line=line_num,
                    column=col_num,
                    severity=severity,
                    message=msg
                )
                diagnostics.append(diag)
                current_diag = diag
            continue

        # Check linker format with line number
        linker_match = LINKER_PATTERN.search(line_str)
        if linker_match:
            line_num = int(linker_match.group(1))
            msg = linker_match.group(2).strip()
            diag = ParsedDiagnostic(
                line=line_num,
                column=None,
                severity="error",
                message=msg
            )
            diagnostics.append(diag)
            current_diag = diag
            continue

        # Check generic linker error without line number
        linker_no_line = LINKER_NO_LINE_PATTERN.search(line_str)
        if linker_no_line and ("undefined reference" in line_str.lower()):
            msg = line_str
            diag = ParsedDiagnostic(
                line=None,
                column=None,
                severity="error",
                message=msg
            )
            diagnostics.append(diag)
            current_diag = diag
            continue

        # If line contains continuation or note text
        if current_diag and (line_str.startswith("note:") or line_str.startswith("suggested")):
            current_diag.notes.append(line_str)

    # Determine primary vs. follow-on errors
    _mark_primary_and_follow_on(diagnostics)

    return diagnostics


def _mark_primary_and_follow_on(diagnostics: List[ParsedDiagnostic]):
    """
    Identifies the primary error and tags subsequent cascading/follow-on errors.
    The first compilation error (non-warning, non-note) is marked as primary.
    Later errors on identical/nearby lines or classic cascading errors are marked as follow-ons.
    """
    primary_found = False
    primary_line: Optional[int] = None

    for diag in diagnostics:
        if diag.severity in ("error", "fatal error"):
            if not primary_found:
                diag.is_primary = True
                diag.is_follow_on = False
                primary_found = True
                primary_line = diag.line
            else:
                diag.is_primary = False
                # If within 2 lines of primary or contains cascading tokens
                is_near = (
                    primary_line is not None and
                    diag.line is not None and
                    abs(diag.line - primary_line) <= 3
                )
                is_cascade_msg = any(cascade_token in diag.message.lower() for cascade_token in [
                    "expected '}' at end of input",
                    "expected ';' before",
                    "expected declaration before",
                    "in expansion of macro",
                    "was not declared in this scope"
                ])

                diag.is_follow_on = is_near or is_cascade_msg
        else:
            # Warnings / notes
            diag.is_primary = False
            diag.is_follow_on = False
