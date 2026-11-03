import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class UndeclaredIdentifierMutator(BaseMutator):
    category = ErrorCategory.UNDECLARED_IDENTIFIER
    name = "undeclared_identifier"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        # Find variables and function calls in main() or helper functions
        # Look for identifiers like tempC, number, fact, sum, count, result, etc.
        id_pattern = re.compile(r"\b([a-zA-Z_][a-zA-Z0-9_]{3,})\b")

        reserved = {
            "include", "iostream", "string", "vector", "using", "namespace", "std",
            "main", "return", "const", "double", "float", "char", "bool", "void",
            "cout", "endl", "cin", "while", "static_cast", "true", "false", "auto"
        }

        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            # Only inside function bodies
            if "#include" in masked or "using namespace" in masked:
                continue

            matches = list(id_pattern.finditer(masked))
            for m in matches:
                ident = m.group(1)
                if ident not in reserved:
                    candidates.append((idx, m.start(1), m.end(1), ident))

        if not candidates:
            return None

        chosen_idx, start, end, ident = rng.choice(candidates)
        orig_line = lines[chosen_idx]

        # Mutate identifier: e.g. append "_misspelled" or typo a character
        variant = "variable_misspell"
        if f"{ident}(" in orig_line:
            variant = "function_call_misspell"
            mutated_ident = ident + "_typo"
        else:
            mutated_ident = ident + "X"

        mutated_line = orig_line[:start] + mutated_ident + orig_line[end:]
        mutated_lines = list(lines)
        mutated_lines[chosen_idx] = mutated_line

        return MutationResult(
            category=self.category.value,
            mutator_name=f"{self.name}.{variant}",
            variant=variant,
            line_no=chosen_idx + 1,
            original_line=orig_line,
            mutated_line=mutated_line,
            mutated_source="\n".join(mutated_lines)
        )
