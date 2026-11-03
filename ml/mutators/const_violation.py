import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class ConstViolationMutator(BaseMutator):
    category = ErrorCategory.CONST_VIOLATION
    name = "const_violation"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        # Find const variables or add an illegal assignment to a const variable
        # Variant 1: find "const type var = val;" and add "var = 999;" right after
        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            match_const = re.search(r"^\s*const\s+(int|double|float|char)\s+([a-zA-Z_]\w*)\s*=\s*([^;]+);", masked)
            if match_const:
                candidates.append((idx, "assign_to_const_var", match_const.group(2)))
                continue

            # Variant 2: find non-const variable that gets modified or passed as ref, and add const keyword
            match_var = re.search(r"^\s*(int|double|long)\s+([a-zA-Z_]\w*)\s*=\s*([^;]+);", masked)
            if match_var and "main" not in masked:
                candidates.append((idx, "add_const_to_modified_var", match_var.group(1)))

        if not candidates:
            return None

        chosen_idx, variant, extra = rng.choice(candidates)
        orig_line = lines[chosen_idx]
        leading = orig_line[:len(orig_line) - len(orig_line.lstrip())]

        if variant == "assign_to_const_var":
            var_name = extra
            mutated_line = f"{orig_line}\n{leading}{var_name} = 999;"
        else: # add_const_to_modified_var
            var_type = extra
            mutated_line = orig_line.replace(var_type, f"const {var_type}", 1)

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
