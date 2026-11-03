import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class InvalidDeclarationMutator(BaseMutator):
    category = ErrorCategory.INVALID_DECLARATION
    name = "invalid_declaration"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            # Find simple local declarations like: const int number = 6; or int sum = 0;
            match = re.search(r"^\s*(const\s+)?(int|double|float|char|bool)\s+([a-zA-Z_]\w*)\s*=\s*([^;]+);", masked)
            if match:
                candidates.append((idx, "redeclare_same_scope", match))
                candidates.append((idx, "void_variable", match))
                candidates.append((idx, "auto_without_init", match))
                candidates.append((idx, "two_types", match))

        if not candidates:
            return None

        chosen_idx, variant, match = rng.choice(candidates)
        orig_line = lines[chosen_idx]
        var_type = match.group(2)
        var_name = match.group(3)
        leading = orig_line[:len(orig_line) - len(orig_line.lstrip())]

        if variant == "redeclare_same_scope":
            mutated_line = f"{orig_line}\n{leading}double {var_name} = 10.5;"
        elif variant == "void_variable":
            mutated_line = f"{leading}void {var_name} = 0;"
        elif variant == "auto_without_init":
            mutated_line = f"{leading}auto {var_name};"
        else: # two_types
            mutated_line = f"{leading}int double {var_name} = 10;"

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
