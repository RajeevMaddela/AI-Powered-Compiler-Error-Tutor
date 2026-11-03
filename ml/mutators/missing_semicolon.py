import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class MissingSemicolonMutator(BaseMutator):
    category = ErrorCategory.MISSING_SEMICOLON
    name = "missing_semicolon"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            # Never mutate for-loop header semicolons
            if "for" in masked and "(" in masked and ";" in masked:
                continue

            stripped = line.rstrip()
            if not stripped.endswith(";"):
                continue

            # Classify variant
            variant = "statement"
            if re.search(r"\b(int|double|float|char|bool|long|auto|string|vector)\b.*=", masked):
                variant = "declaration"
            elif re.search(r"\b(cout|cin|std::cout|std::cin)\b", masked):
                variant = "io_statement"
            elif re.search(r"\breturn\b", masked):
                variant = "return_statement"
            elif stripped.endswith("};"):
                variant = "struct_or_class_end"

            candidates.append((idx, variant))

        if not candidates:
            return None

        # Deterministic choice using rng
        chosen_idx, variant = rng.choice(candidates)
        orig_line = lines[chosen_idx]
        
        # Strip the last semicolon
        last_semi_pos = orig_line.rfind(";")
        if last_semi_pos == -1:
            return None

        mutated_line = orig_line[:last_semi_pos] + orig_line[last_semi_pos+1:]
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
