import re
from typing import Optional, List
from ml.mutators.base import BaseMutator, MutationResult, mask_strings_and_comments
from backend.app.compiler.constants import ErrorCategory

class WrongArgumentsMutator(BaseMutator):
    category = ErrorCategory.WRONG_ARGUMENTS
    name = "wrong_arguments"

    def apply(self, source: str, rng) -> Optional[MutationResult]:
        lines = source.splitlines()
        candidates = []

        # Find function call sites in main: e.g. fn(arg1, arg2) or fn(arg1)
        # Match pattern: identifier(args)
        for idx, line in enumerate(lines):
            masked = mask_strings_and_comments(line)
            # Match call inside main: e.g. int res = computeGCD(x, y); or double t = toKelvin(val);
            match = re.search(r"\b([a-zA-Z_]\w*)\s*\(([^;\{\}\(\)]+)\);", masked)
            if match and "main" not in match.group(1) and "cout" not in match.group(1) and "cin" not in match.group(1):
                candidates.append((idx, match))

        if not candidates:
            return None

        chosen_idx, match = rng.choice(candidates)
        orig_line = lines[chosen_idx]
        fn_name = match.group(1)
        args_str = match.group(2)

        variants = ["drop_argument", "extra_argument", "type_argument"]
        variant = rng.choice(variants)

        if variant == "drop_argument":
            # If comma present, drop one; else call with no args
            if "," in args_str:
                new_args = args_str.split(",")[0]
            else:
                new_args = ""
        elif variant == "extra_argument":
            new_args = args_str + ', "unexpected_extra_arg"'
        else: # type_argument
            new_args = '"wrong_string_argument"'

        call_orig = f"{fn_name}({args_str})"
        call_new = f"{fn_name}({new_args})"
        mutated_line = orig_line.replace(call_orig, call_new, 1)

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
