import cx_Freeze

executables = [cx_Freeze.Executable(script="main.py",
                                    targetName="ghsm.exe")]

include_files = ["settings.py"]

cx_Freeze.setup(
    name="GHSM",
    options={
        "build_exe": {
            "include_files": include_files
        }
    },
    executables=executables
)
