# AG Reasoning Framework

This repository implements the Assume Guarantee (AG) Reasoning framework using Angluin's L* algorithm for learning deterministic finite automata (DFA), considering the domain of autonomous vehicles and related decision processes. It includes various optimisation methods to enhance the efficiency of the learning process.

## Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Project Structure](#project-structure)
- [Optimisation Methods](#optimisation-methods)
- [Examples](#examples)
- [References](#references)

## Installation

To set up the project, Python 3.6+ must be installed.

## Usage

The main functional directory, considering the three optimisation methods referenced from Chaki & Strichman are situated within the ag_opt directory. 

Novel optimisation methods four and five are situated in opt_4 and opt_5 directories, respectively. 

Navigate to the respective directory and run the run_ag.py script to execute the AG reasoning process. 

It must be noted that the ag directory is simply L* based AG Reasoning without any form of optimisation or subsequent related alterations. 

It also must be noted that ag includes standardised unit testing functions and opt_5 includes context-aware adjustment functionality.

## Configuration

Configuration settings are managed using Hydra. You can find the configuration files in the conf directory of each optimisation method. Modify the YAML files to change parameters such as search depth, maximum length, and the number of runs.

## Optimisation Methods

### Optimisation Method 1: Reusing Counterexamples

This method reuses counterexamples from previous iterations to avoid redundant queries and speed up the learning process.

### Optimisation Method 2: Selective Membership Queries

This method optimises the learning process by selectively performing membership queries based on a predefined threshold.

### Optimisation Method 3: Alphabet Minimisation

This method minimises the assumption alphabet to improve the learning process efficiency.

### Optimisation Method 4: Adaptive Query Selection

This method dynamically selects queries based on the current state of the learning process to improve efficiency.

### Optimisation Method 5: Reuse of Counterexamples

This method improves the hypothesis merging process to reduce the number of iterations required for convergence.


## References

Angluin, D. (1987). Learning Regular Sets from Queries and Counterexamples. Information and Computation.

Clarke, E. M., Grumberg, O., & Peled, D. (1999). Model Checking. MIT Press.

Peled, D. (2001). Software Reliability Methods. Springer.

Chandra, S., & Jhala, R. (2008). Learning Assumptions for Compositional Verification. ACM SIGPLAN Notices.

Clarke, E. M., & Zuliani, P. (2011). Statistical Model Checking for Cyber-Physical Systems. Automated Technology for Verification and Analysis.

Steffen, B., & Lüttgen, G. (2002). Property-Driven Design and Verification. Formal Methods in System Design.

Alur, R., & Henzinger, T. A. (1999). Reactive Modules. Formal Methods in System Design.

Vardi, M. Y. (1995). An Automata-Theoretic Approach to Linear Temporal Logic. Banff Higher Order Workshop.

Holzmann, G. J. (2004). The SPIN Model Checker: Primer and Reference Manual. Addison-Wesley Professional.

Chaki, S., & Strichman, O. (2007). Optimized L* Learning for Assume-Guarantee Reasoning. In Proceedings of the 19th International Conference on Computer Aided Verification (
CAV).