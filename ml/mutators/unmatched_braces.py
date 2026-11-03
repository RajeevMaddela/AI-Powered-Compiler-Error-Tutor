import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class UnmatchedBracesMutator(BaseMutator):
    category = ErrorCategory.UNMATCHED_BRACES
    name = "unmatched_braces"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            if "{" in masked:
                candidates.append((idx, "delete_open_brace", "{"))
            if "}" in masked:
                candidates.append((idx, "delete_close_brace", "}"))
            if line.strip() == "return 0;":
                candidates.append((idx, "insert_extra_close_brace", None))

        if not candidates:
            return None

        chosen_idx, variant, target = rng.choice(candidates)
        orig_line = lines[chosen_idx]

        if variant == "delete_open_brace":
            pos = orig_line.find("{")
            mutated_line = orig_line[:pos] + orig_line[pos+1:]
        elif variant == "delete_close_brace":
            pos = orig_line.rfind("}")
            mutated_line = orig_line[:pos] + orig_line[pos+1:]
        else: # insert_extra_close_brace
            leading = orig_line[:len(orig_line) - len(orig_line.lstrip())]
            mutated_line = f"{leading}}}\n{orig_line}"

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
