import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class UndefinedReferenceMutator(BaseMutator):
    category = ErrorCategory.UNDEFINED_REFERENCE
    name = "undefined_reference"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        
        # Look for helper function defined below main
        # Find where main ends
        main_end_idx = -1
        in_main = False
        depth = 0
        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            if "int main(" in masked:
                in_main = True
            if in_main:
                depth += masked.count("{") - masked.count("}")
                if depth == 0 and "}" in masked:
                    main_end_idx = idx
                    break

        if main_end_idx == -1 or main_end_idx >= len(lines) - 2:
            return None

        # Helper function starts after main_end_idx
        # Let's find definition header below main
        def_idx = -1
        for idx in range(main_end_idx + 1, len(lines)):
            line = lines[idx]
            if re.search(r"^\s*(int|double|long|long long|bool|string|void)\s+[a-zA-Z_]\w*\s*\(", line):
                def_idx = idx
                break

        if def_idx == -1:
            return None

        variants = ["remove_definition", "mismatch_param_type"]
        variant = rng.choice(variants)
        orig_line = lines[def_idx]

        mutated_lines = list(lines)
        if variant == "remove_definition":
            # Comment out the entire definition from def_idx to end of file
            for i in range(def_idx, len(mutated_lines)):
                mutated_lines[i] = "// " + mutated_lines[i]
            mutated_line = "// [definition removed] " + orig_line
        else: # mismatch_param_type
            # Change param type in definition, e.g. int -> char* or double -> int
            if "int" in orig_line:
                mutated_line = orig_line.replace("int", "char*", 1)
            elif "double" in orig_line:
                mutated_line = orig_line.replace("double", "float*", 1)
            else:
                mutated_line = orig_line.replace("(", "(double dummy, ", 1)
            mutated_lines[def_idx] = mutated_line

        return MutationResult(
            category=self.category.value,
            mutator_name=f"{self.name}.{variant}",
            variant=variant,
            line_no=def_idx + 1,
            original_line=orig_line,
            mutated_line=mutated_line,
            mutated_source="\n".join(mutated_lines)
        )
