import os
import tempfile
import docker

def test_broken_code():
    client = docker.from_env()
    with tempfile.TemporaryDirectory() as temp_dir:
        file_path = os.path.join(temp_dir, "main.cpp")
        source_code = '#include <iostream>\nint main() {\n  int x = 10\n  std::cout << y << std::endl;\n  return 0;\n}\n'
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(source_code)

        container = client.containers.create(
            image="tutor-sandbox:latest",
            command=[
                "g++",
                "-std=c++17",
                "-Wall",
                "-Wextra",
                "-fno-diagnostics-show-caret",
                "-fmessage-length=0",
                "-fdiagnostics-color=never",
                "/workspace/main.cpp",
                "-o",
                "/tmp/a.out"
            ],
            network_mode="none",
            mem_limit="256m",
            memswap_limit="256m",
            pids_limit=64,
            read_only=True,
            tmpfs={
                "/tmp": "rw,noexec,nosuid,size=64m"
            },
            volumes={
                temp_dir: {"bind": "/workspace", "mode": "ro"}
            },
            user="10001",
            cap_drop=["ALL"],
            security_opt=["no-new-privileges:true"],
            environment={"LC_ALL": "C", "LANG": "C"}
        )

        try:
            container.start()
            result = container.wait(timeout=10)
            logs = container.logs(stdout=True, stderr=True).decode("utf-8", errors="replace")
            exit_code = result.get("StatusCode", 0)
            print("Exit code:", exit_code)
            print("Output logs:\n" + logs)
        finally:
            container.remove(force=True)

if __name__ == "__main__":
    test_broken_code()
