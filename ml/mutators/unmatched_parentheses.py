import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class UnmatchedParenthesesMutator(BaseMutator):
    category = ErrorCategory.UNMATCHED_PARENTHESES
    name = "unmatched_parentheses"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            if "#include" in masked:
                continue

            # If condition or while condition
            if re.search(r"\b(if|while)\s*\(", masked) and ")" in masked:
                candidates.append((idx, "delete_paren_condition", ")"))
            elif "(" in masked and ")" in masked and ("cout" in masked or ";" in masked):
                candidates.append((idx, "delete_paren_call", ")"))
            elif "(" in masked:
                candidates.append((idx, "delete_open_paren", "("))
            elif ")" in masked and ";" in masked:
                candidates.append((idx, "insert_extra_paren", None))

        if not candidates:
            return None

        chosen_idx, variant, target = rng.choice(candidates)
        orig_line = lines[chosen_idx]

        if variant == "delete_paren_condition":
            pos = orig_line.rfind(")")
            mutated_line = orig_line[:pos] + orig_line[pos+1:]
        elif variant == "delete_paren_call":
            pos = orig_line.rfind(")")
            mutated_line = orig_line[:pos] + orig_line[pos+1:]
        elif variant == "delete_open_paren":
            pos = orig_line.find("(")
            mutated_line = orig_line[:pos] + orig_line[pos+1:]
        else: # insert_extra_paren
            pos = orig_line.rfind(")")
            mutated_line = orig_line[:pos] + "))" + orig_line[pos+1:]

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
