Compile using:

javac BenchmarkHarness.java

Requires Java 7 or above.

Run using:

java BenchmarkHarness benchmark_name input_size

If input size isn't specified then it runs using the default workload. deltablue and richards workloads cannot be adjusted.

benchmark_name and default workloads are:

binarytrees 13

deltablue

fannkuchredux 9

fasta 150000

knucleotide 150000

mandelbrot 500

nbody 100000

regexdna 150000

revcomp 150000

richards

spectralnorm 160

all (runs all benchmarks using default workload size)