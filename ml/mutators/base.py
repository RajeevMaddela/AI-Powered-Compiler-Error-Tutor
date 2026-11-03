import re
from dataclasses import dataclass
from typing import Optional, List, Tuple
from abc import ABC, abstractmethod
from backend.app.compiler.constants import ErrorCategory

@dataclass
class MutationResult:
    category: str
    mutator_name: str
    variant: str
    line_no: int
    original_line: str
    mutated_line: str
    mutated_source: str

def is_comment_or_string_only(line: str) -> bool:
    stripped = line.strip()
    if not stripped or stripped.startswith("//") or stripped.startswith("/*") or stripped.startswith("*"):
        return True
    return False

def mask_strings_and_comments(line: str) -> str:
    """
    Replaces string literals and comments with spaces of equal length
    so indices remain identical but operations won't match inside strings/comments.
    """
    out = list(line)
    in_string = False
    escape = False
    for i, ch in enumerate(out):
        if not in_string:
            if ch == '"':
                in_string = True
            elif ch == '/' and i + 1 < len(out) and out[i+1] == '/':
                # Line comment till end
                for j in range(i, len(out)):
                    out[j] = ' '
                break
        else:
            if escape:
                escape = False
                out[i] = ' '
            elif ch == '\\':
                escape = True
                out[i] = ' '
            elif ch == '"':
                in_string = False
            else:
                out[i] = ' '
    return "".join(out)

class BaseMutator(ABC):
    category: ErrorCategory
    name: str

    @abstractmethod
    def apply(self, source: str, rng) -> Optional[MutationResult]:
        """
        Applies a mutation to the given source code deterministically using rng.
        Returns MutationResult if successful, or None if the mutation cannot be applied.
        """
        pass
