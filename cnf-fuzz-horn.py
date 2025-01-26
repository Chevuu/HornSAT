#!/usr/bin/env python3
 
import os
import sys
import random
import argparse
from multiprocessing.pool import ThreadPool

def parse_cnf_file(filepath):
    """Parse a CNF file and return its metadata and clauses."""
    with open(filepath, 'r') as file:
        lines = file.readlines()

    header = None
    clauses = []

    for line in lines:
        line = line.strip()
        if line.startswith('p cnf'):
            header = line
        elif line and not line.startswith('c'):
            clauses.append(list(map(int, line.split()[:-1])))

    return header, clauses

def is_clause_satisfied(clause, solution):
    """Check if a clause is satisfied by the current solution."""
    return any(solution[abs(lit)] == (lit > 0) for lit in clause)

def count_horn_clauses(clauses):
    """Count the number of horn clauses (clauses with at most 1 positive literal)."""
    return sum(1 for clause in clauses if len([lit for lit in clause if lit > 0]) <= 1)

def generate_solution(clauses, num_vars):
    """Generate an initial solution based on the first occurrence of literals."""
    solution = {}
    for clause in clauses:
        for lit in clause:
            var = abs(lit)
            if var not in solution:
                solution[var] = (lit > 0)
                if len(solution) == num_vars:
                    break
        if len(solution) == num_vars:
            break

    # If there are still unset variables, assign random values to the remaining
    for var in range(1, num_vars + 1):
        if var not in solution:
            solution[var] = random.choice([True, False])

    return solution

def make_satisfiable(clauses, num_vars, target_horn_count):
    """Ensure the set of clauses is satisfiable while keeping horn clause count as close as possible."""
    solution = generate_solution(clauses, num_vars)

    current_horn_count = count_horn_clauses(clauses)

    for clause in clauses:
        if is_clause_satisfied(clause, solution):
            continue

        positive_literals = [(i, lit) for i, lit in enumerate(clause) if lit > 0]
        negative_literals = [(i, lit) for i, lit in enumerate(clause) if lit < 0]

        if current_horn_count <= target_horn_count:
            if len(positive_literals) > 1:
                for index, lit in positive_literals:
                    if not (is_clause_satisfied(clause, solution)) and solution[abs(lit)] == False:
                        clause[index] = -abs(lit)
                if is_clause_satisfied(clause, solution) and len([lit for lit in clause if lit > 0]) <= 1:
                    current_horn_count += 1
            else:
                if is_clause_satisfied(clause, solution):
                    continue
                else:
                    for index, lit in positive_literals:
                        if not (is_clause_satisfied(clause, solution)) and solution[abs(lit)] == False:
                            clause[index] = -abs(lit)
                    for index, lit in negative_literals:
                        if not (is_clause_satisfied(clause, solution)) and solution[abs(lit)] == True:
                            clause[index] = abs(lit)

                    if is_clause_satisfied(clause, solution) and len([lit for lit in clause if lit > 0]) > 1:
                        current_horn_count -= 1
        else:
            if len(positive_literals) > 1:
                if is_clause_satisfied(clause, solution):
                    continue
                for index, lit in negative_literals:
                    if solution[abs(lit)] == True:
                        clause[index] = abs(lit)
                for index, lit in positive_literals:
                    if not (is_clause_satisfied(clause, solution)) and solution[abs(lit)] == False:
                        clause[index] = -abs(lit)
                if is_clause_satisfied(clause, solution) and len([lit for lit in clause if lit > 0]) <= 1:
                    current_horn_count += 1
            else:
                if not (is_clause_satisfied(clause, solution)):
                    for index, lit in negative_literals:
                        if solution[abs(lit)] == True:
                            clause[index] = abs(lit)
                    for index, lit in positive_literals:
                        if not (is_clause_satisfied(clause, solution)) and solution[abs(lit)] == False:
                            clause[index] = -abs(lit)

                    if is_clause_satisfied(clause, solution) and len([lit for lit in clause if lit > 0]) > 1:
                        current_horn_count -= 1

    return clauses

def create_horn_instances(header, clauses, output_folder, base_filename, threads, count):
    """Generate CNF instances with varying numbers of horn clauses."""
    _, _, num_vars, num_clauses = header.split()
    num_vars = int(num_vars)
    num_clauses = int(num_clauses)
    step = max(num_clauses // count, 1)

    def generate_instance(i):
        target_horn_clauses = i * step
        modified_clauses = [clause[:] for clause in clauses]  # Deep copy

        # Adjust clauses to match the target horn clause count
        horn_count = count_horn_clauses(modified_clauses)

        if horn_count < target_horn_clauses:
            for clause in modified_clauses:
                if horn_count >= target_horn_clauses:
                    break
                positive_literals = [lit for lit in clause if lit > 0]
                if len(positive_literals) > 1:
                    for lit_to_flip in positive_literals[:-1]:
                        clause[clause.index(lit_to_flip)] = -lit_to_flip
                    horn_count += 1

        elif horn_count > target_horn_clauses:
            for clause in modified_clauses:
                if horn_count <= target_horn_clauses:
                    break
                if len([lit for lit in clause if lit > 0]) <= 1:
                    neg_literals = [lit for lit in clause if lit < 0]
                    for lit_to_flip in neg_literals[:2]:
                        clause[clause.index(lit_to_flip)] = abs(lit_to_flip)
                    if len([lit for lit in clause if lit > 0]) >= 2:
                        horn_count -= 1

        if (random.random() < 0.75):
            sat_clauses = make_satisfiable(modified_clauses, num_vars, target_horn_clauses)
        else:
            # Use the modified clauses directly without guaranteeing satisfiability
            sat_clauses = modified_clauses

        # Write the modified instance to a CNF file
        cnf_string = f"{header}\n"
        cnf_string += "c t mc\n"
        for clause in sat_clauses:
            cnf_string += " ".join(map(str, clause)) + " 0\n"

        output_file = os.path.join(output_folder, f"{base_filename}_{i:03d}.cnf")
        with open(output_file, 'w') as f:
            f.write(cnf_string)

    # Parallelize instance generation
    with ThreadPool(threads) as pool:
        pool.map(generate_instance, range(count))

def process_input_file(input_file, output_folder, threads, count):
    """Process a single CNF file and generate horn instances."""
    header, clauses = parse_cnf_file(input_file)
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    create_horn_instances(header, clauses, output_folder, base_filename, threads, count)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate CNF instances with varying numbers of horn clauses.")
    parser.add_argument("--input", type=str, required=True, help="Path to the input CNF file.")
    parser.add_argument("--output", type=str, required=True, help="Path to the folder to save output CNF files.")
    parser.add_argument("--threads", type=int, default=4, help="Number of threads for parallel execution.")
    parser.add_argument("--count", type=int, default=100, help="Number of instances to generate.")
    parser.add_argument("--seed", type=int, default=None, help="Set the random seed (default: None).")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    os.makedirs(args.output, exist_ok=True)
    process_input_file(args.input, args.output, args.threads, args.count)
