import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult
from backend.app.compiler.constants import ErrorCategory

class MissingHeaderMutator(BaseMutator):
    category = ErrorCategory.MISSING_HEADER
    name = "missing_header"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        for idx, line in enumerate(lines):
            match = re.search(r"^\s*#include\s*<([^>]+)>", line)
            if match:
                header = match.group(1)
                candidates.append((idx, header))

        if not candidates:
            return None

        chosen_idx, header = rng.choice(candidates)
        orig_line = lines[chosen_idx]
        mutated_line = f"// omitted header: <{header}>"

        mutated_lines = list(lines)
        mutated_lines[chosen_idx] = mutated_line

        return MutationResult(
            category=self.category.value,
            mutator_name=f"{self.name}.remove_{header}",
            variant=f"remove_{header}",
            line_no=chosen_idx + 1,
            original_line=orig_line,
            mutated_line=mutated_line,
            mutated_source="\n".join(mutated_lines)
        )
