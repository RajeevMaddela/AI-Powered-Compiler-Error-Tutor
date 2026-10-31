import pytest
from fastapi import HTTPException
from backend.app.sandbox.runner import run_code_in_sandbox
from backend.app.core.config import settings

def test_huge_input_rejected():
    """
    Abuse test: Oversized input payload exceeding 64KB cap must be rejected with 413.
    """
    huge_code = "// comment\n" * 10000  # > 100 KB
    with pytest.raises(HTTPException) as exc_info:
        run_code_in_sandbox(huge_code)
    assert exc_info.value.status_code == 413
    assert "exceeds maximum allowed size" in exc_info.value.detail

def test_endless_template_recursion():
    """
    Abuse test: Infinite template instantiation recursion must terminate safely
    without freezing the server.
    """
    recursive_code = """
    template<int N>
    struct Recursive {
        static constexpr int val = Recursive<N + 1>::val;
    };

    int main() {
        return Recursive<0>::val;
    }
    """
    res = run_code_in_sandbox(recursive_code)
    # Must fail compilation safely
    assert res.exit_code != 0
    assert not res.is_clean
    # Should catch template recursion depth or timeout safely
    assert ("template instantiation depth" in res.output.lower() or
            "timed out" in res.output.lower() or
            "fatal error" in res.output.lower() or
            "error:" in res.output.lower())

def test_huge_memory_constexpr():
    """
    Abuse test: Attempting to allocate gigantic memory in compiler.
    Must be killed or rejected by container limits with non-zero exit code.
    """
    memory_bomb = """
    char arr[30000000000ULL] = {1};
    int main() {
        return arr[0];
    }
    """
    res = run_code_in_sandbox(memory_bomb)
    assert res.exit_code != 0
    assert not res.is_clean

def test_giant_output_truncated():
    """
    Abuse test: High volume compiler diagnostics must be safely capped
    at 128KB without memory exhaustion.
    """
    output_bomb = """
    #define M1(x) int x; int x;
    #define M2(x) M1(x##0) M1(x##1) M1(x##2) M1(x##3)
    #define M3(x) M2(x##0) M2(x##1) M2(x##2) M2(x##3)
    #define M4(x) M3(x##0) M3(x##1) M3(x##2) M3(x##3)
    #define M5(x) M4(x##0) M4(x##1) M4(x##2) M4(x##3)
    M5(a)
    int main() { return 0; }
    """
    res = run_code_in_sandbox(output_bomb)
    assert res.exit_code != 0
    # Output must not exceed settings max output bytes
    assert len(res.output.encode("utf-8")) <= settings.SANDBOX_MAX_OUTPUT_BYTES + 200

def test_system_file_include():
    """
    Abuse test: Attempting to leak system files through #include directives.
    Must fail safely without disclosing sensitive content.
    """
    exploit_code = """
    #include </etc/shadow>
    int main() {
        return 0;
    }
    """
    res = run_code_in_sandbox(exploit_code)
    assert res.exit_code != 0
    # Must never include credentials
    assert "root:" not in res.output

def test_clean_compilation():
    """
    Positive baseline: Valid C++17 program compiles cleanly with exit code 0.
    """
    clean_code = """
    #include <iostream>
    int main() {
        std::cout << "Clean" << std::endl;
        return 0;
    }
    """
    res = run_code_in_sandbox(clean_code)
    assert res.exit_code == 0
    assert res.is_clean is True
    assert not res.timed_out
