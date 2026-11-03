import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class TypeMismatchMutator(BaseMutator):
    category = ErrorCategory.TYPE_MISMATCH
    name = "type_mismatch"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        # Find integer declarations/assignments: int var = expr; or return expr in int/double fn
        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            
            # Match int/long/double declaration with init
            match_init = re.search(r"\b(int|long|long long|double|float)\s+([a-zA-Z_]\w*)\s*=\s*([^;]+);", masked)
            if match_init:
                candidates.append((idx, "init_string_to_numeric", match_init))
                continue

            # Match return in int/double function
            if re.search(r"^\s*return\s+([a-zA-Z0-9_\+\-\*\/\s\.]+);", masked) and "main" not in masked:
                candidates.append((idx, "return_string_mismatch", None))

        if not candidates:
            return None

        chosen_idx, variant, match_obj = rng.choice(candidates)
        orig_line = lines[chosen_idx]

        if variant == "init_string_to_numeric" and match_obj:
            # Replace initializer with "error_string"
            var_type = match_obj.group(1)
            var_name = match_obj.group(2)
            leading = orig_line[:orig_line.find(var_type)]
            mutated_line = f'{leading}{var_type} {var_name} = "incompatible_type_string";'
        else:
            leading = orig_line[:len(orig_line) - len(orig_line.lstrip())]
            mutated_line = f'{leading}return "incompatible_return_value";'

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
