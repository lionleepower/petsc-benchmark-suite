# AGENTS.md

## Project purpose

This repository is used for learning and benchmarking PETSc, MPI, and OpenMP concepts. Prefer incremental, educational changes over large automatic refactors.

## Safety rules

* Do not modify or overwrite original reference files under `resources/` unless explicitly requested.
* Do not delete existing files.
* Do not use `sudo`.
* Do not install system packages automatically.
* Before editing files, list the files that will be changed.
* After editing files, summarize the changes and provide validation commands.

## Documentation rules

* Keep explanations suitable for a learner rebuilding their HPC foundations.
* Explain the mathematical meaning of PETSc examples before discussing performance optimisation.
* Distinguish local WSL commands from HPC cluster commands.
* Use English comments in code and scripts.
* Keep tutorial material under `tutorial/`.

## Script rules

* Prefer small scripts with one clear purpose.
* Add comments for commands, environment variables, and adjustable parameters.
* Validate scripts using the smallest reasonable test case before introducing scaling experiments.
