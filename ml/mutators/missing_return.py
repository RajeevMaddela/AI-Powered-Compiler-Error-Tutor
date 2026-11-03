import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class MissingReturnMutator(BaseMutator):
    category = ErrorCategory.MISSING_RETURN
    name = "missing_return"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        # Find return statements in non-main functions
        in_main = False
        non_main_fn = False
        brace_depth = 0

        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)

            if "int main(" in masked:
                in_main = True

            # Match function headers like: double celsiusToFahrenheit(double c) {
            if not in_main and re.search(r"\b(int|double|long|long long|bool|string|char|vector<[^>]+>)\s+[a-zA-Z_]\w*\s*\(", masked) and ";" not in masked:
                non_main_fn = True

            if "{" in masked:
                brace_depth += masked.count("{")
            if "}" in masked:
                brace_depth -= masked.count("}")
                if brace_depth <= 0:
                    in_main = False
                    non_main_fn = False

            if non_main_fn and not in_main:
                if re.search(r"^\s*return\s+[^;]+;", masked):
                    candidates.append((idx, "delete_return"))
                    candidates.append((idx, "empty_return"))

        if not candidates:
            return None

        chosen_idx, variant = rng.choice(candidates)
        orig_line = lines[chosen_idx]

        if variant == "delete_return":
            # Remove the return statement completely (or replace with comment)
            leading = orig_line[:len(orig_line) - len(orig_line.lstrip())]
            mutated_line = f"{leading}// return statement omitted"
        else: # empty_return
            leading = orig_line[:len(orig_line) - len(orig_line.lstrip())]
            mutated_line = f"{leading}return;"

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
