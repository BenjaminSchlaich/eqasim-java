
# stream lines from the file data/slurm-54443250_final_everything.out
# until a line contains the substring "ITERATION 60 BEGINS"
# from there on store the lines into a new file data/iter60.out
def extract_iteration_60(input_file_path, output_file_path):
    with open(input_file_path, 'r') as infile, open(output_file_path, 'w') as outfile:
        copy_lines = False
        for line in infile:
            if "ITERATION 60 BEGINS" in line:
                copy_lines = True
            if copy_lines:
                outfile.write(line)

# remove empty lines from file and store the result in the same file again.
def remove_empty_lines(file_path):
    with open(file_path, 'r') as infile:
        lines = infile.readlines()
    with open(file_path, 'w') as outfile:
        for line in lines:
            if line.strip():  # only write non-empty lines
                outfile.write(line)

# load the numbers from the file data/iter60.out and return their median
def load_numbers_and_median(file_path):
    numbers = []
    with open(file_path, 'r') as infile:
        for line in infile:
            try:
                number = float(line.strip())
                numbers.append(number)
            except ValueError:
                continue  # skip lines that cannot be converted to float
    if numbers:
        numbers.sort()
        n = len(numbers)
        if n % 2 == 0:
            return (numbers[n//2 - 1] + numbers[n//2]) / 2
        else:
            return numbers[n//2]
    else:
        return None

# extract_iteration_60('data/slurm-54443250_final_everything.out', 'data/iter60.out')

# remove_empty_lines('data/iter60 copy.out')

print(load_numbers_and_median('data/iter60 copy.out'))
