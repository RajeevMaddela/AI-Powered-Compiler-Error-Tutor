from typing import List, Dict
from ml.mutators.base import BaseMutator, MutationResult
from ml.mutators.missing_semicolon import MissingSemicolonMutator
from ml.mutators.undeclared_identifier import UndeclaredIdentifierMutator
from ml.mutators.type_mismatch import TypeMismatchMutator
from ml.mutators.unmatched_braces import UnmatchedBracesMutator
from ml.mutators.unmatched_parentheses import UnmatchedParenthesesMutator
from ml.mutators.missing_return import MissingReturnMutator
from ml.mutators.invalid_declaration import InvalidDeclarationMutator
from ml.mutators.missing_header import MissingHeaderMutator
from ml.mutators.missing_namespace import MissingNamespaceMutator
from ml.mutators.undefined_reference import UndefinedReferenceMutator
from ml.mutators.wrong_arguments import WrongArgumentsMutator
from ml.mutators.const_violation import ConstViolationMutator
from backend.app.compiler.constants import ErrorCategory

ALL_MUTATORS: List[BaseMutator] = [
    MissingSemicolonMutator(),
    UndeclaredIdentifierMutator(),
    TypeMismatchMutator(),
    UnmatchedBracesMutator(),
    UnmatchedParenthesesMutator(),
    MissingReturnMutator(),
    InvalidDeclarationMutator(),
    MissingHeaderMutator(),
    MissingNamespaceMutator(),
    UndefinedReferenceMutator(),
    WrongArgumentsMutator(),
    ConstViolationMutator(),
]

MUTATORS_BY_CATEGORY: Dict[str, BaseMutator] = {
    m.category.value: m for m in ALL_MUTATORS
}

def get_mutator(category_name: str) -> BaseMutator:
    return MUTATORS_BY_CATEGORY[category_name]
