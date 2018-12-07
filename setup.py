import cx_Freeze

executables = [cx_Freeze.Executable(script="src/main.py",
                                    targetName="ghsm.exe")]

include_files = ["src"]

cx_Freeze.setup(
    name="GHSM",
    options={
        "build_exe": {
            "include_files": include_files
        }
    },
    executables=executables
)
