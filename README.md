# Horn Clause Generator

This repository contains a single Python script (`cnf-fuzz-horn.py`) that generates Conjunctive Normal Form (CNF) formulas in the DIMACS format. The generator systematically varies the fraction of Horn clauses across the entire range (0% to 100%). This tool is designed for benchmarking model counting solvers and enables detailed exploration of solver performance under diverse structural configurations.

## Features

- Generates CNF formulas in **DIMACS** format.
- Systematic control over the fraction of Horn clauses (0% to 100%).
- Stabilizes additional structural features for meaningful benchmarking.
- Randomness tied to a **seed** for reproducibility.

## Stable Features

The following structural features are monitored and stabilized during generation while `horn-clauses-fraction` is ranged across full feature space:

| Feature Name          | Description                                                    |
|-----------------------|----------------------------------------------------------------|
| `vars-clauses-ratio`    | Ratio of variables to clauses.                                 |
| `VCG-VAR-mean`          | Mean variable node degree in the Variable Clause Graph.        |
| `VCG-CLAUSE-mean`       | Mean clause node degree in the Variable Clause Graph.         |
| `cluster-coeff-mean`    | Mean weighted clustering coefficient in the Variable Clause Graph. |
| `reducedClauses `       | Number of clauses remaining after preprocessing.              |
| `reducedVars`           | Number of variables remaining after preprocessing.            |
| `BINARY+`              | Fraction of clauses with 2 or more literals.                  |
| `TRINARY+`            | Fraction of clauses with 3 or more literals.                  |

## Parameters

| Parameter             | Type      | Default | Description                                                              |
|-----------------------|-----------|---------|--------------------------------------------------------------------------|
| `--input`             | `str`     | N/A     | Path to the input CNF file.                                              |
| `--output`            | `str`     | N/A     | Directory to save the generated CNF files.                               |
| `--threads`           | `int`     | `4`     | Number of threads for parallel generation.                               |
| `--count`             | `int`     | `100`   | Number of CNF instances to generate.                                     |
| `--seed`              | `int`     | `None`  | Set the random seed for reproducibility.                                 |

## Integration with SharpVelvet

Horn Clause Generator is not designed to integrate easily with [SharpVelvet](https://github.com/meelgroup/SharpVelvet). To use this generator within SharpVelvet, future implementation needs to be added on SharpVelvet side.

## Output Format

Generated CNF formulas are output in the standard DIMACS format. Example:

```
p cnf 3 5
c t mc
-3 -1 0
2 -1 0
-2 0
-2 1 0
1 3 2 0
```

This specifies a formula with 3 variables and 5 clauses.

## Usage

To use the Horn Clause Generator, run the following command:

```bash
python path/to/cnf-fuzz-horn.py --input path/to/base_instance.cnf --output path/to/out_folder --threads <num_threads> --count 100
```

### Example

```bash
python cnf-fuzz-horn.py --input instances/base.cnf --output generated_instances --threads 4 --count 100
```

This will generate 100 CNF files with varying Horn-clause fractions in the `generated_instances` folder, based of of the `base.cnf` instance.

## Research Data

Inside our paper **Feature-Driven SAT Instance Generation**, three sets of instances are mentioned in Section 7. These sets ca be found in ./instances folder. In it are 3-CNF instances with 400 clauses and 90 variables, 100 vraibles and 110 variables respectively.

## Citing

```
@software{HornSAT,
  author = {Vuk Jurišić},
  title = {Horn Generator},
  url = {https://github.com/Chevuu/HornSAT},
  date = {2025-01-26},
}
```
