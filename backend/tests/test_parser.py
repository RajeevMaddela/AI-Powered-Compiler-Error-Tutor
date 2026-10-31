import pytest
from backend.app.compiler.parser import parse_compiler_output

def test_parse_clean_output():
    diagnostics = parse_compiler_output("")
    assert diagnostics == []

def test_parse_single_syntax_error():
    sample_output = """/workspace/main.cpp:4:3: error: expected ';' before 'return'
    """
    diags = parse_compiler_output(sample_output)
    assert len(diags) == 1
    d = diags[0]
    assert d.line == 4
    assert d.column == 3
    assert d.severity == "error"
    assert "expected ';'" in d.message
    assert d.is_primary is True
    assert d.is_follow_on is False

def test_parse_multi_errors_primary_vs_followon():
    sample_output = """/workspace/main.cpp:4:3: error: expected ',' or ';' before 'std'
/workspace/main.cpp:5:10: error: 'undeclared_var' was not declared in this scope
/workspace/main.cpp:6:1: error: expected '}' at end of input
    """
    diags = parse_compiler_output(sample_output)
    assert len(diags) == 3

    # First syntax error must be primary
    assert diags[0].is_primary is True
    assert diags[0].is_follow_on is False
    assert diags[0].line == 4

    # Second error within 1 line is follow-on
    assert diags[1].is_primary is False
    assert diags[1].is_follow_on is True

    # Third error is classic cascading syntax breakdown
    assert diags[2].is_primary is False
    assert diags[2].is_follow_on is True

def test_parse_notes_attached_to_error():
    sample_output = """/workspace/main.cpp:6:5: error: 'cout' was not declared in this scope
/workspace/main.cpp:6:5: note: 'std::cout' is defined in header '<iostream>'
    """
    diags = parse_compiler_output(sample_output)
    assert len(diags) == 1
    assert diags[0].line == 6
    assert len(diags[0].notes) == 1
    assert "<iostream>" in diags[0].notes[0]

def test_parse_linker_error():
    sample_output = """/usr/lib/gcc/x86_64-alpine-linux-musl/13.2.1/../../../../x86_64-alpine-linux-musl/bin/ld: /tmp/cca.o: in function 'main':
/workspace/main.cpp:4: undefined reference to 'non_existent_function()'
    """
    diags = parse_compiler_output(sample_output)
    assert len(diags) == 1
    assert diags[0].line == 4
    assert "undefined reference to" in diags[0].message
