# CATAStrophy

[![PyPI version](https://badge.fury.io/py/catastrophy.svg)](https://badge.fury.io/py/catastrophy)
[![Anaconda-Server Badge](https://anaconda.org/darcyabjones/catastrophy/badges/version.svg)](https://anaconda.org/darcyabjones/catastrophy)
[![Build Status](https://travis-ci.org/ccdmb/catastrophy.svg?branch=master)](https://travis-ci.org/ccdmb/catastrophy)

<img src="https://raw.githubusercontent.com/ccdmb/catastrophy/master/catastrophy_hero.png" width=200 />

CATAStrophy is a classification method for describing lifestyles/trophic characteristics
of filamentous plant pathogens using carbohydrate-active enzymes (CAZymes).
The name CATAStrophy is a backronym portmanteau hybrid where "CATAS" means
CAZyme Assisted Training And Sorting.

CATAStrophy takes HMMER3 files from searches against the [dbCAN](http://bcb.unl.edu/dbCAN2/) CAZyme database
as input and returns a pseudo-probabilities called the relative centroid distance (RCD) of trophic class memberships for each file.

To "train" this models, we performed principal component analysis (PCA) on the frequencies of CAZymes for a set of curated proteomes with literature support for their trophic lifestyles.
For each class in our classification system, we find the center/geometric mean of the class in the first 16 principal components.

New proteomes are classified by transforming the CAZyme frequencies using the same PCA loadings as in the training set.
We then find the closest class center in PCA space, and set that RCD score to 1.
Then for each of the other classes we find the distance between the new proteome and the class center divided (i.e. relative to) by the distance to the closest class center.
If a new proteome is equidistant between two class centroids and they are closer than any other class, then both RCD scores will be one, so the RCD method is a _kind_ of multi-label classifier.
This is useful when evaluating your organism, because it might have characteristics of multiple classes (or be so dissimilar to any class that the distance is meaningless).


## Installing

CATAStrophy is a python program which can be used as a python module or via a command-line interface.
It can be installed from PyPI <https://pypi.org/project/catastrophy/> using [pip](https://pip.pypa.io/en/stable/), or from anaconda <https://anaconda.org/darcyabjones/catastrophy> using [conda](https://docs.conda.io/en/latest/).

Users that are less familiar with python and pip might like to read our [INSTALL.md](INSTALL.md) document, which explains things in more detail, including where this will be installed and using virtual environments.
For details on installing and using conda see their [getting-started guide](https://docs.conda.io/projects/conda/en/latest/user-guide/overview.html).

CATAStrophy is tested to work with python 3.6+, and it depends on [numpy](http://www.numpy.org/) and [BioPython](https://biopython.org/).

To install CATAStrophy and dependencies with pip:

```bash
# Windows users may need to subtitute "Python" instead of "python3"
python3 -m pip install --user catastrophy
```

To install CATAStrophy and dependencies using conda:

```bash
conda install -c darcyabjones catastrophy
```

## Using CATAStrophy

The to run CATAStrophy you need to supply the input files and where to put the output.
Catastrophy uses [HMMER3](http://hmmer.org/) `hmmscan` searches against dbCAN as input.

Either the plain text (stdout) and "domain table" (`--domtblout`) can be used.

The easiest way to get a file like this is to annotate your proteome using
the dbCAN online tool at <http://cys.bios.niu.edu/dbCAN2/>, and
save the HMMER3 raw text results locally.

Assuming that you have this file locally you can run CATAStrophy like so:

```bash
catastrophy -i my_dbcan_results.txt -f hmmer -o my_catastrophy_results.csv
```

The output will be a tab-delimited file (which you can open in excel) with
the first row containing column headers and subsequent rows containing a
label and the pseudo-probabilities of membership to each trophic class.
The `-f/--format` flag specified the format of the input file and defaults to `hmmer`.

NOTE: In this document I use the `.csv` extension to mean any plain text tabular
format because excel doesn't recognise alternate extensions like `.tsv`.
The domain table output is actually space delimited and the catastrophy
output is a tab delimited file.

By default the filenames are used as the label but you can explicitly specify
a label using the `-l/--label` flag. The output from the command above will
have two lines, one containing the column headers and the other containing
results for the file `my_dbcan_results.txt` which will have the label
"my_dbcan_results.txt".
If you don't specify a label for stdin input the label will be "<stdin>".

To give it a nicer label you can run this.

```bash
catastrophy -i my_dbcan_results.txt -l prettier_label -o my_catastrophy_results.csv
```

Which would give the output line for `my_dbcan_results.txt` the label "prettier_label".
Labels cannot contain spaces unless you explicitly escape them (quotes will not work).

Multiple input files can be provided using spaces to separate them:

```bash
catastrophy -i dbcan_1.txt dbcan_2.txt -o my_catastrophy_results.csv
```

The output from this will contain three rows, one containing the headers and
the other two containing the results for the files `dbcan_1.txt` and `dbcan_2.txt`
which will be labelled by the filenames.
Note that standard bash "globbing" patterns expand into a space delimited array,
so you can easily use `*` or subshells if you like (eg. `$(find . -type f -name *.txt)` etc).
To explicitly label these files you can again supply the label flag with the space separated labels.

```bash
catastrophy -i dbcan_1.txt dbcan_2.txt -l label1 label2 -o my_catastrophy_results.csv
```

Note that if you do use the label flag, the number of labels **must** be the same as the number of input files.


Finally because dbCAN is updated as new CAZyme classes are created, merged,
or split, catastrophy has a final parameter that allows you to select the
model trained on a specific dbCAN version (starting from version 5).

To specify the version of the model to use, include the `-m/--model`
flag with one of the valid options (see `catastrophy -h` for the options).

```bash
catastrophy -m v5 -i my_dbcan_results.txt -o my_catastrophy_results.csv
```

The model versions just reflect the version of dbCAN that the model was trained against.


## Running dbCAN locally

If you have lots of proteomes to run (or you're a command-line snob like me)
then you probably don't want to use the web interface.
In that case you can run the dbCAN pipeline locally using [HMMER](http://hmmer.org/).

The instructions for running the HMMER and the dbCAN parser can be found here
<http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-old@UGA/> in the `readme.txt` file.
It isn't the most friendly documentation though so i'll repeat it here
(assuming that you've installed [HMMER](http://hmmer.org/) and are using a unix-like OS).

First download the HMMs and the parser script.

```bash
cd <a directory that you can work in>

mkdir -p ./data
wget -qc -P ./data http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-HMMdb-V7.txt
```

Note that I'm downloading a specific version of the database rather that just the latest one.
Now we can convert the file containing HMM definitions into a HMMER database.

```bash
hmmpress ./data/dbCAN-HMMdb-V7.txt
```

Now we can run HMMER to find matches to the dbCAN HMMs.
For demonstration, we'll save both the domain table and plain text outputs.

```bash
hmmscan --domtblout my_fasta_hmmer.csv ./data/dbCAN-HMMdb-V7.txt my_fasta.fasta > my_fasta_hmmer.txt
```

The domain table is now in the file `my_fasta_hmmer.csv` and the plain hmmer
text output is in `my_fasta_hmmer.txt`.
Either one of these files is appropriate for use with CATAStrophy, (just
remember to specify the `--format` flag).

```bash
catastrophy -m v7 -i my_fasta_hmmer.csv --format domtab -o my_catastrophy_results.csv

# or
catastrophy -m v7 -i my_fasta_hmmer.txt --format hmmer -o my_catastrophy_results.csv
```


## Command line arguments

Only the input files are required and are provided as positional arguments.
Other optional parameters are below:

| Parameter | default | description |
| :---      | :---    | :---        |
| `-h`/`--help` | flag | Show help text and exit. |
| `--version` | flag | Show program version information and exit. |
| `-f`/`--format` | "hmmer_text" | The format that the input is provided in. All input files must be in the same format. HMMER raw (hmmer_text, default) and domain table (hmmer_domtab) formatted files are accepted. Files processed by the dbCAN formatter `hmmscan-parser.sh` are also accepted using the `dbcan` option. |
| `-l`/`--label` | filenames | Label to give the prediction for the input file(s). Specify more than one label by separating them with a space. The number of labels should be the same as the number of input files.  By default, the filenames are used as labels. |
| `-o`/`--outfile` | stdout | File path to write tab delimited output to. |
| `-m`/`--model` | latest | The version of the model (matching the dbCAN database version) to use. The latest version is used by default. See `catastrophy -h` for list of valid options. |
| `-m`/`--nomenclature` | nomenclature3 | The nomenclature type to use. Nomenclature1 is the classical symbiont, saprotroph, (hemi)biotroph, necrotroph system. Nomenclature2 separates wilts from necrotrophs, and considers symbionts as a class of biotroph. Nomenclature3 is the system proposed in the paper. See `catastrophy -h` for list of options.|


Basic usage:

```bash
# To stdout aka "-o -"
catastrophy infile1.txt infile2.txt > results.csv

# To specify an output filename
catastrophy -o results.csv infile1.txt infile2.txt

# To take input from stdin use a "-"
cat infile1.txt | catastrophy - > results.csv

# If you provide labels you may need to use "--"
# to tell when you're done and that infiles should start.
# This is because both "--label" and infiles can take multiple arguments.

catastrophy -l mylabel1 mylabel2 -o results.csv infile1.txt infile2.txt  # Fine
catastrophy -o results.csv -l mylabel1 mylabel2 infile1.txt infile2.txt  # Dangerous
# Do this instead to tell where labels stops and infiles starts.
catastrophy -o results.csv -l mylabel1 mylabel2 -- infile1.txt infile2.txt
```


## Output

Output will be as a tab-separated values file, with each input file as a row
and each trophic class as a column.

For example, for nomenclature1 the table might look like.

```bash
catastrophy infile1.txt infile2.txt
```

| label | saprotroph | biotroph 1 | biotroph 2 | biotroph 3 | mesotroph - internal | mesotroph - external | necrotroph - narrow | necrotroph - broad | wilt |
| :---  | ---:       | ---:       | ---:       | ---:       | ---:                 | ---:                 | ---:                | ---:               | ---: |
| infile1.txt | 0.1 | 0.1 | 0.9 | 1 | 0.3 | 0.3 | 0.1 | 0.1 | 0.1 |
| infile2.txt | 0.1 | 0.1 | 0.2 | 0.2 | 0.8 | 0.4 | 0.1 | 0.6 | 0.1 |
