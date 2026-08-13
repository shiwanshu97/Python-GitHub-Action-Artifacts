# GitHub Actions Self-Hosted Runner on macOS (Apple Silicon)

## Objective

Set up a GitHub Actions self-hosted runner on an Apple Silicon Mac, troubleshoot the runner, configure the Python environment, and successfully execute a Python GitHub Actions workflow.

---

# Part 1: Check Mac Architecture

## 1. Check the Mac architecture

Checked the CPU architecture of the Mac to determine which GitHub Actions runner should be downloaded.

    uname -m

Output:

    arm64

The Mac is using Apple Silicon.

Therefore, the required GitHub Actions runner is:

    osx-arm64

The `osx-x64` runner should not be used on this Mac.

---

## 2. Check macOS version

Checked the macOS version running on the machine.

    sw_vers

Output:

    ProductName:        macOS
    ProductVersion:     26.6.1
    BuildVersion:       25G76

---

# Part 2: Initial GitHub Actions Runner Setup

## 3. Initial runner downloaded

Initially downloaded the x64 version of the GitHub Actions runner.

    actions-runner-osx-x64-2.336.0.tar.gz

However, the Mac architecture was:

    arm64

This was an architecture mismatch.

---

## 4. Initial CoreCLR error

When trying to configure or start the runner, the following error occurred:

    Failed to create CoreCLR, HRESULT: 0x80070057

The problem was caused by using the x64 runner on an Apple Silicon ARM64 Mac.

---

## 5. Remove the incorrect runner

Removed the old runner directory.

    rm -rf actions-runner

Created the directory again.

    mkdir actions-runner
    cd actions-runner

---

## 6. Download the ARM64 runner

Downloaded the correct ARM64 GitHub Actions runner.

    curl -o actions-runner-osx-arm64-2.336.0.tar.gz \
    -L https://github.com/actions/runner/releases/download/v2.336.0/actions-runner-osx-arm64-2.336.0.tar.gz

---

## 7. Extract the runner

Extracted the downloaded runner package.

    tar xzf actions-runner-osx-arm64-2.336.0.tar.gz

---

## 8. Verify runner architecture

Checked the architecture of the runner executable.

    file bin/Runner.Listener

Output:

    Mach-O 64-bit executable arm64

This confirmed that the correct ARM64 runner was installed.

---

# Part 3: Investigating the CoreCLR Problem

## 9. Check CoreCLR libraries

Checked whether the required CoreCLR libraries existed.

    find . -type f \( \
    -name 'libcoreclr.dylib' \
    -o -name 'libhostfxr.dylib' \
    -o -name 'libhostpolicy.dylib' \
    \) -print

Output:

    ./bin/libcoreclr.dylib
    ./bin/libhostfxr.dylib
    ./bin/libhostpolicy.dylib

The required CoreCLR libraries were present.

---

## 10. Verify CoreCLR architecture

Checked the architecture of the CoreCLR libraries.

    file bin/libcoreclr.dylib bin/libhostfxr.dylib bin/libhostpolicy.dylib

Output showed:

    Mach-O 64-bit dynamically linked shared library arm64

This confirmed that the CoreCLR libraries were also compiled for ARM64.

---

## 11. Check Runner.Listener.dll

Checked whether the runner's .NET assembly was present.

    find . -type f -name 'Runner.Listener.dll' -print

Output:

    ./bin/Runner.Listener.dll

---

## 12. Check temporary directory

Checked the macOS temporary directory.

    echo $TMPDIR

Output:

    /var/folders/vp/vwvvh1h53h76kqqb3swphwjc0000gn/T/

---

## 13. Check CoreCLR dependencies

Checked the dependencies of `libcoreclr.dylib`.

    otool -L bin/libcoreclr.dylib

The library referenced standard macOS frameworks such as:

    Foundation.framework
    CoreFoundation.framework
    CoreServices.framework
    Security.framework
    libSystem.B.dylib
    libc++.1.dylib
    libobjc.A.dylib

---

## 14. Check CoreCLR code signature

Checked the code signature of the CoreCLR library.

    codesign -dv --verbose=4 bin/libcoreclr.dylib 2>&1 | head -30

Important output:

    Format=Mach-O thin (arm64)
    Signature=adhoc

---

## 15. Check extended attributes

Checked whether macOS had attached quarantine attributes to the CoreCLR library.

    xattr -l bin/libcoreclr.dylib

No quarantine attribute was found.

---

## 16. Check system dotnet installation

Checked whether `dotnet` was installed globally on the Mac.

    dotnet --info

Output:

    zsh: command not found: dotnet

Also checked:

    dotnet --version

Output:

    zsh: command not found: dotnet

The GitHub Actions runner contains its own required .NET runtime, so a system-wide `dotnet` command was not required.

---

## 17. Check for bundled dotnet executable

Checked whether a standalone `dotnet` executable existed inside the runner.

    find externals -maxdepth 3 -type f -name 'dotnet' -exec file {} \;

No standalone `dotnet` executable was found.

---

## 18. Check runner external components

Checked the `externals` directory.

    ls -lah externals

The directory contained:

    node20
    node24

---

## 19. Check CoreCLR runtime

Used runtime tracing to investigate the CoreCLR startup problem.

    COREHOST_TRACE=1 ./bin/Runner.Listener --version

---

## 20. Check dynamic libraries

Used macOS dynamic library tracing.

    DYLD_PRINT_LIBRARIES=1 ./bin/Runner.Listener --version 2>&1

The output showed that libraries including `libclrjit.dylib` were being loaded before CoreCLR failed.

---

## 21. Check libclrjit architecture

Checked the architecture of `libclrjit.dylib`.

    file bin/libclrjit.dylib

Output:

    Mach-O 64-bit dynamically linked shared library arm64

---

## 22. Check libclrjit dependencies

Checked the dependencies of `libclrjit.dylib`.

    otool -L bin/libclrjit.dylib

The dependencies were standard macOS libraries and frameworks.

---

## 23. Check relevant environment variables

Checked for custom .NET and dynamic loader environment variables.

    env | grep -E '^(DOTNET|CORECLR|COREHOST|ComPlus|DYLD|TMPDIR)'

No custom `DOTNET`, `CORECLR`, `COREHOST`, `ComPlus`, or `DYLD` variables were present.

---

# Part 4: Fix the Runner Directory Path

## 24. Identify the original runner path

The runner was initially located under:

    /Users/shiwanshu/Downloads/HeroViered/DevOps/CI:CD/GitHub Actions/actions-runner

The path contained:

    CI:CD

and:

    GitHub Actions

The special character `:` and spaces in the path were causing problems with the runner runtime in this environment.

---

## 25. Rename CI:CD

Changed:

    CI:CD

to:

    CICD

---

## 26. Rename GitHub Actions

Changed:

    GitHub Actions

to:

    GitHubActions

---

## 27. Final runner path

The final runner path became:

    /Users/shiwanshu/Downloads/HeroViered/DevOps/CICD/GitHubActions/actions-runner

Checked the current directory.

    pwd

Output:

    /Users/shiwanshu/Downloads/HeroViered/DevOps/CICD/GitHubActions/actions-runner

---

## 28. Verify the runner after changing the path

Ran:

    ./bin/Runner.Listener --version

Output:

    2.336.0

This confirmed that the CoreCLR problem was resolved.

---

# Part 5: Configure the GitHub Actions Runner

## 29. Configure the runner

Created the self-hosted runner from:

    GitHub Repository
    -> Settings
    -> Actions
    -> Runners
    -> New self-hosted runner

Selected:

    macOS
    ARM64

Then configured the runner using:

    ./config.sh --url https://github.com/<USERNAME>/<REPOSITORY> --token <RUNNER_TOKEN>

Example:

    ./config.sh --url https://github.com/shiwanshu97/Python-GitHub-Action-Artifacts --token <RUNNER_TOKEN>

The runner token should never be committed to Git or shared publicly.

---

# Part 6: Start the Self-Hosted Runner

## 30. Start the runner

Started the GitHub Actions self-hosted runner.

    ./run.sh

The runner connects to GitHub and waits for jobs.

The terminal running `run.sh` must remain open while the runner is being used.

---

# Part 7: Initial Python GitHub Actions Workflow

## 31. Initial workflow

The initial workflow used `actions/setup-python@v5`.

    name: Python Artifact Demo

    on:
      push:
        branches:
          - main
      workflow_dispatch:

    jobs:
      Create-Artifact:
        runs-on: self-hosted

        steps:
          - name: Checkout repository
            uses: actions/checkout@v4

          - name: Setup Python
            uses: actions/setup-python@v5
            with:
              python-version: '3.11'

          - name: Run Python program
            run: python app.py

          - name: Show generated file
            run: cat result.txt

          - name: Upload result as artifact
            uses: actions/upload-artifact@v4
            with:
              name: python-result-file
              path: result.txt

---

# Part 8: Python Setup Error

## 32. Python 3.11 download

The workflow successfully detected that Python 3.11 was not available in the local cache.

It downloaded:

    python-3.11.9-darwin-arm64.tar.gz

This confirmed that the runner was correctly recognized as a Darwin ARM64 runner.

---

## 33. Python tool-cache error

The workflow then failed with:

    Creating Python hostedtoolcache folder...

    Error: mkdir: /Users/runner: Permission denied

The failure occurred during:

    actions/setup-python@v5

---

## 34. Why the error happened

The self-hosted runner was running under the local Mac user:

    /Users/shiwanshu

But `actions/setup-python@v5` attempted to create its tool-cache under:

    /Users/runner

The local user did not have permission to create that directory.

Therefore, the Python setup action failed.

---

# Part 9: First Python Tool Cache Workaround

## 35. Configure RUNNER_TOOL_CACHE

Tried configuring a local tool cache:

    - name: Configure Python tool cache
      run: |
        echo "RUNNER_TOOL_CACHE=$RUNNER_TEMP/_toolcache" >> "$GITHUB_ENV"
        mkdir -p "$RUNNER_TEMP/_toolcache"

This created the tool-cache directory under the runner's temporary directory.

However, `actions/setup-python@v5` still attempted to create:

    /Users/runner

and the workflow continued to fail.

Therefore, this workaround did not resolve the issue.

---

# Part 10: Final Python Solution

## 36. Use the Mac's existing Python

Since Python was already installed on the Mac, we removed:

    actions/setup-python@v5

and used the locally installed:

    python3

directly.

This avoided the `/Users/runner` tool-cache problem.

---

## 37. Check Python version

Run:

    python3 --version

Then check the Python executable:

    which python3

Example output:

    Python 3.11.x

and:

    /opt/homebrew/bin/python3

---

# Part 11: Final Working GitHub Actions Workflow

## 38. Final workflow

The final workflow is:

    name: Python Artifact Demo

    on:
      push:
        branches:
          - main
      workflow_dispatch:

    jobs:
      Create-Artifact:
        runs-on: self-hosted

        steps:
          - name: Checkout repository
            uses: actions/checkout@v4

          - name: Check Python
            run: |
              echo "Python location:"
              which python3
              echo "Python version:"
              python3 --version

          - name: Run Python program
            run: |
              python3 app.py

          - name: Show generated file
            run: |
              cat result.txt

          - name: Upload result as artifact
            uses: actions/upload-artifact@v4
            with:
              name: python-result-file
              path: result.txt

---

# Part 12: Explanation of the Final Workflow

## 39. Checkout Repository

The following step downloads the repository source code onto the self-hosted runner.

    - name: Checkout repository
      uses: actions/checkout@v4

---

## 40. Check Python

The following step checks where Python is installed and which version is being used.

    - name: Check Python
      run: |
        echo "Python location:"
        which python3
        echo "Python version:"
        python3 --version

---

## 41. Run Python Application

The Python application is executed using the locally installed Python.

    - name: Run Python program
      run: |
        python3 app.py

---

## 42. Show Generated File

The workflow displays the generated `result.txt` file in the GitHub Actions log.

    - name: Show generated file
      run: |
        cat result.txt

---

## 43. Upload Artifact

The generated file is uploaded as a GitHub Actions artifact.

    - name: Upload result as artifact
      uses: actions/upload-artifact@v4
      with:
        name: python-result-file
        path: result.txt

The artifact can be downloaded from the GitHub Actions workflow run.

---

# Part 13: Node 20 Warning

## 44. Node 20 deprecation warning

The workflow displayed:

    Node 20 is being deprecated.
    This workflow is running with Node 24 by default.

This was only a warning.

It was not responsible for the Python failure.

The runner automatically used Node 24.

---

# Part 14: Punycode Warning

## 45. Punycode warning

The workflow also displayed:

    [DEP0040] DeprecationWarning: The `punycode` module is deprecated.

This was also only a warning.

It was not responsible for the Python failure.

---

# Part 15: Actual Python Error

## 46. Actual error

The actual failure was:

    mkdir: /Users/runner: Permission denied

The error came from:

    actions/setup-python@v5

because it attempted to use:

    /Users/runner

as the Python tool-cache location.

The final solution was to use:

    python3

from the local Mac installation instead of:

    actions/setup-python@v5

---

# Part 16: Final Working Environment

## 47. Operating System

    macOS 26.6.1

---

## 48. Mac Architecture

    arm64

---

## 49. GitHub Actions Runner

    2.336.0

---

## 50. Runner Architecture

    osx-arm64

---

## 51. Runner Directory

    /Users/shiwanshu/Downloads/HeroViered/DevOps/CICD/GitHubActions/actions-runner

---

## 52. Runner Verification

Run:

    ./bin/Runner.Listener --version

Expected output:

    2.336.0

---

## 53. Start Runner

Run:

    ./run.sh

---

## 54. Python

Use:

    python3

---

# Part 17: Troubleshooting Summary

| Problem | Cause | Resolution |
|---|---|---|
| CoreCLR error | x64 runner was used on ARM64 Mac | Downloaded `osx-arm64` runner |
| CoreCLR continued failing | Runner was inside a problematic path containing `:` and spaces | Changed `CI:CD` to `CICD` and `GitHub Actions` to `GitHubActions` |
| Runner architecture issue | Mac requires ARM64 runner | Verified with `file bin/Runner.Listener` |
| CoreCLR libraries | Required ARM64 libraries | Verified using `file` |
| Runner verification | CoreCLR needed to work correctly | `Runner.Listener --version` returned `2.336.0` |
| Python setup failed | `actions/setup-python` attempted to use `/Users/runner` | Removed `actions/setup-python` |
| Node 20 warning | Node deprecation warning | Ignored because it was not an error |
| Punycode warning | Node dependency warning | Ignored because it was not an error |

---

# Part 18: Final Architecture

The final setup works like this:

    Developer
        |
        | git push
        v
    GitHub Repository
        |
        | GitHub Actions Workflow
        v
    Self-Hosted Runner
    macOS Apple Silicon
        |
        | checkout
        v
    Python Application
        |
        | python3 app.py
        v
    result.txt
        |
        | upload-artifact@v4
        v
    GitHub Actions Artifact

---

# Part 19: Key Lessons Learned

## 55. Match Runner Architecture

For Apple Silicon:

    arm64 -> osx-arm64

For Intel Mac:

    x86_64 -> osx-x64

Always check the Mac architecture before downloading the runner.

---

## 56. Keep Runner Paths Simple

Recommended:

    ~/github-actions-runner

Avoid paths containing:

    :
    spaces

For example, avoid:

    CI:CD
    GitHub Actions
    My Runner

Prefer:

    CICD
    GitHubActions
    MyRunner

---

## 57. Self-Hosted Runner Uses Your Machine

A self-hosted runner uses the machine where the runner is installed.

It uses the machine's:

- CPU
- RAM
- Disk
- Operating System
- Installed Software
- Python Installation
- Permissions
- Network

---

## 58. Separate Runner Problems From Workflow Problems

The CoreCLR problem was a runner startup problem.

The `/Users/runner` error was a Python setup problem.

These were two separate issues.

---

## 59. Warnings Are Different From Errors

Warnings:

    Node 20 is being deprecated.

and:

    [DEP0040] DeprecationWarning: The `punycode` module is deprecated.

Actual error:

    mkdir: /Users/runner: Permission denied

Always identify the actual `Error:` message when troubleshooting a GitHub Actions workflow.

---

# Part 20: Final Status

    Mac Architecture       -> arm64
    Runner Architecture    -> osx-arm64
    Runner Version         -> 2.336.0
    CoreCLR                -> Working
    Runner.Listener        -> Working
    Runner Path            -> Clean
    Self-Hosted Runner     -> Working
    Python                 -> Local python3
    GitHub Actions         -> Ready
    Artifact Upload        -> Configured

The macOS Apple Silicon self-hosted GitHub Actions runner is configured and ready for the Python Artifact assignment.
