import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class MissingNamespaceMutator(BaseMutator):
    category = ErrorCategory.MISSING_NAMESPACE
    name = "missing_namespace"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        # Variant 1: Remove "using namespace std;"
        for idx, line in enumerate(lines):
            if re.search(r"^\s*using\s+namespace\s+std\s*;", line):
                candidates.append((idx, "remove_using_namespace_std", None))

        # Variant 2: Strip std:: prefix from std::cout, std::vector, std::string, etc.
        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            matches = list(re.finditer(r"\bstd::", masked))
            for m in matches:
                candidates.append((idx, "remove_std_prefix", m.start()))

        if not candidates:
            return None

        chosen = rng.choice(candidates)
        chosen_idx = chosen[0]
        variant = chosen[1]
        orig_line = lines[chosen_idx]

        if variant == "remove_using_namespace_std":
            mutated_line = "// omitted: using namespace std;"
        else: # remove_std_prefix
            pos = chosen[2]
            mutated_line = orig_line[:pos] + orig_line[pos+5:]

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
