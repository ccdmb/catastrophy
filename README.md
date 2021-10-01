<img src="https://raw.githubusercontent.com/ccdmb/catastrophy/master/catastrophy_hero.png" width=200 />

# CATAStrophy

[![PyPI version](https://badge.fury.io/py/catastrophy.svg)](https://badge.fury.io/py/catastrophy)
[![Anaconda-Server Badge](https://anaconda.org/darcyabjones/catastrophy/badges/version.svg)](https://anaconda.org/darcyabjones/catastrophy)


CATAStrophy is a classification method for describing lifestyles/trophic characteristics
of filamentous plant pathogens using carbohydrate-active enzymes (CAZymes).
The name CATAStrophy is a backronym portmanteau hybrid where "CATAS" means
CAZyme Assisted Training And Sorting.

CATAStrophy takes HMMER3 files from searches against the [dbCAN](http://bcb.unl.edu/dbCAN2/) CAZyme database
as input and returns a pseudo-probabilities called the relative centroid distance (RCD) of trophic class memberships for each file.

To train these models, we performed principal component analysis (PCA) on the frequencies of CAZymes for a set of curated proteomes with literature support for their trophic lifestyles.
For each class in our classification system, we find the centre/geometric mean of the class in the first 16 principal components.

New proteomes are classified by transforming the CAZyme frequencies using the same PCA loadings as in the training set.
We then find the closest class center in PCA space, and set that RCD score to 1.
Then for each of the other classes we find the distance between the new proteome and the class center divided (i.e. relative to) by the distance to the closest class center.
If a new proteome is equidistant between two class centroids and they are closer than any other class, then both RCD scores will be one, so the RCD method is a _kind_ of multi-label classifier.
This is useful when evaluating your organism, because it might have characteristics of multiple classes (or be so dissimilar to any class that the distance is meaningless).


## Citation and further information

The CATAStrophy method and trophic classification systems is described [here](https://doi.org/10.3389/fmicb.2019.03088):

James K. Hane, Jonathan Paxman, Darcy A. B. Jones, Richard P. Oliver and Pierre de Wit (2020). "CATAStrophy", a Genome-Informed Trophic Classification of Filamentous Plant Pathogens – How Many Different Types of Filamentous Plant Pathogens Are There? _Frontiers in Microbiology_. doi: [10.3389/fmicb.2019.03088](https://doi.org/10.3389/fmicb.2019.03088)


## Installing

CATAStrophy is a python program which can be used as a python module or via a command-line interface.
It can be installed from PyPI <https://pypi.org/project/catastrophy/> using [pip](https://pip.pypa.io/en/stable/), or from anaconda <https://anaconda.org/darcyabjones/catastrophy> using [conda](https://docs.conda.io/en/latest/).

Users that are less familiar with python and pip might like to read our [INSTALL.md](https://github.com/ccdmb/catastrophy/blob/master/INSTALL.md) document which explains things in more detail, including where things will be installed and how to use virtual environments.
For details on installing and using conda see their [getting-started guide](https://docs.conda.io/projects/conda/en/latest/user-guide/getting-started.html).

CATAStrophy is tested to work with python 3.6+, and it depends on [numpy](http://www.numpy.org/) and [BioPython](https://biopython.org/).

To install CATAStrophy and dependencies with pip:

```bash
# Windows users may need to use "Python" instead of "python3"
python3 -m pip install --user catastrophy
```

To install CATAStrophy and dependencies using conda:

```bash
conda install -c darcyabjones catastrophy
```

## Using CATAStrophy

To run CATAStrophy you need to supply the input files and where to put the output.
Catastrophy uses [HMMER3](http://hmmer.org/) `hmmscan` searches against dbCAN as input.
Either the plain text (stdout) or "domain table" (`--domtblout`) outputs can be used.

The easiest way to get a HMMER3 plain text file is to annotate your proteome using
the dbCAN online tool at <http://bcb.unl.edu/dbCAN2/blast.php> (make sure the HMMER tool is selected to run), and
save the HMMER3 raw text (Select the HMMER tab, then "Download Raw HMMER output") results locally.

> **WARNING**: Before you run any dbCAN searches, please [read the section below on database versions](https://github.com/ccdmb/catastrophy#database-versions).

Assuming that you have this file locally you can run CATAStrophy like so:

```bash
catastrophy -f hmmer -o my_catastrophy_results.csv my_dbcan_results.txt
```

The input files are provided as positional arguments after all of the optional parameters.
The output will be a tab-delimited file (which you can open in excel) containing RCD results for each nomenclature and trophic class for each of the input files.
The `-f/--format` flag specified the format of the input file and defaults to `hmmer`.


Multiple input files can be provided using spaces to separate them:

```bash
catastrophy -o my_catastrophy_results.csv dbcan_1.txt dbcan_2.txt
```

Note that standard bash "globbing" patterns expand into a space delimited array,
so you can easily use `*` or subshells if you like (eg. `$(find . -type f -name *.txt)` etc).


### Database versions

CATAStrophy models are specific to the different versions of [dbCAN](http://bcb.unl.edu/dbCAN2/).
CAZyme family frequencies are at the core of the CATAStrophy method, so adding, removing, or changing the database HMMs will necessarily affect the results.
CATAStrophy will attempt to check for mismatched model versions and alert you, but could potentially give inaccurate results if a mismatch isn't detected.

**It is very important that you match the database version with the CATAStrophy model.**

To specify the version of the model to use, include the `-m/--model`
flag with one of the valid options (`v4`, `v5`, `v6`, `v7`, or `v8`;see `catastrophy -h` for the available model versions in your installation).

```bash
catastrophy --model v7 -o my_catastrophy_results.csv my_dbcan_results.txt
```

The model versions just reflect the version of dbCAN that the model was trained against (i.e. dbCAN 7 would use CATAStrophy model v7).

> **NOTE:**
> The dbCAN2 web-server will always search against the latest version of dbCAN.
> To find the latest version number, go to <http://bcb.unl.edu/dbCAN2/download/Databases/> and find the file with the highest number with the pattern `dbCAN-HMMdb-V8.txt`.
> If we haven't yet trained a model for the latest version of dbCAN please contact us.
> Otherwise you may need to [run HMMER yourself](#running-dbcan-locally).

The CATAStrophy paper used version 6 of dbCAN, you may get slightly different results with different database versions.


### Output

Output will be as a tab-separated values file, with the columns for the filename, nomenclature, nomenclature class, and the RCD value.
Each possible combination of label, nomenclature and class is listed in a [long format](https://en.wikipedia.org/wiki/Wide_and_narrow_data).

For example, part of the table might look like this:

```bash
catastrophy infile1.txt infile2.txt
```

| label       | nomenclature | class | value |
| :---        | ---:         | ---:  | ---:  |
| infile1.txt | nomenclature1 | saprotroph | 0.9 |
| infile2.txt | nomenclature1 | monomertroph1 | 0.2 |


### Labels

By default the filenames (including directories and extensions) are used as the label in the output, but you can explicitly specify
a label using the `-l/--label` flag. The output from the command above will
have two lines, one containing the column headers and the other containing
results for the file `my_dbcan_results.txt` which will have the label
"my_dbcan_results.txt".
If you don't specify a label for stdin input the label will be "\<stdin\>".

To give it a nicer label you can run this.

```bash
catastrophy -l prettier_label -o my_catastrophy_results.csv my_dbcan_results.txt
```

Which would give the output line for `my_dbcan_results.txt` the label "prettier_label".
Labels cannot contain spaces unless you explicitly escape them (quotes will not work).

To label multiple input files you can again supply the label flag with the space separated labels.

```bash
catastrophy -l label1 label2 -o my_catastrophy_results.csv dbcan_1.txt dbcan_2.txt
```

Note that if you do use the label flag, the number of labels **must** be the same as the number of input files.


If you provide the `--label` as the last argument before the input positional arguments (`infiles`) you may need to use `--`
to tell when you're done and that infiles should start.
This is because both `--label` and infiles can take multiple arguments.

```bash
catastrophy -l mylabel1 mylabel2 -o results.csv infile1.txt infile2.txt  # Fine
catastrophy -o results.csv -l mylabel1 mylabel2 infile1.txt infile2.txt  # Dangerous

# Do this instead to tell where labels stops and infiles starts.
catastrophy -o results.csv -l mylabel1 mylabel2 -- infile1.txt infile2.txt
```


## Running dbCAN locally

If you have lots of proteomes to run or CATAStrophy hasn't been trained on the latest version of dbCAN yet, then you probably don't want to use the web interface.
In that case you can run the dbCAN pipeline locally using [HMMER](http://hmmer.org/).

There is a pipeline available at [https://github.com/ccdmb/catastrophy-pipeline](https://github.com/ccdmb/catastrophy-pipeline) that can automate much of the following steps for you.

The following steps assume that you've installed [HMMER](http://hmmer.org/) and are using a unix-like OS.

#### Step 1. Download dbCAN.

We first need to download the dbCAN database (HMMs) to search against.
You will need to make sure that you download a version of dbCAN that it compatible with CATAStrophy.
To get a list of databases versions that is supported, you can use the `--help` flag and look for the `--nomenclature` help section.

```bash
catastrophy --help
```

Once you've identified the version you want to use, download the database from <http://bcb.unl.edu/dbCAN2/download/Databases/>.
Alternatively you can use the bash commands below to download it, setting the value of `DBCAN_VERSION` to the desired version (NB. the full url **must** match one of the file names in <http://bcb.unl.edu/dbCAN2/download/Databases/>).


```bash
DBCAN_VERSION="V7"

mkdir -p ./data
wget -qc -P ./data "http://bcb.unl.edu/dbCAN2/download/Databases/dbCAN-HMMdb-${DBCAN_VERSION}.txt"
```


#### Step 2. Prepare the dbCAN HMM database

Now we can convert the file containing HMM definitions into a HMMER database.

```bash
hmmpress ./data/dbCAN-HMMdb-V7.txt
```

This will create several files at the same location as the `.txt` file, so it's good to do this
inside a separate folder (as we've done here).


#### Step 3. Search your proteomes against the dbCAN HMMs.

Now we can run HMMER `hmmscan` to find matches to the dbCAN HMMs.
For demonstration, we'll save both the domain table and plain text outputs.

```bash
hmmscan --domtblout my_fasta_hmmer.csv ./data/dbCAN-HMMdb-V7.txt my_fasta.fasta > my_fasta_hmmer.txt
```

The domain table is now in the file `my_fasta_hmmer.csv` and the plain hmmer
text output is in `my_fasta_hmmer.txt`.
Either one of these files is appropriate for use with CATAStrophy (just
remember to specify the `--format` flag).


#### Step 4. Classify your proteomes using CATAStrophy.

Now we can finally find out what CATAStrophy thinks our organism is!

To use the files created in step 3, you can run either of the following commands.
Remember to match the version of dbCAN with the model version in catastrophy.

```bash
catastrophy --model v7 --format domtab -o my_catastrophy_results.csv my_fasta_hmmer.csv

# or
catastrophy --model v7 --format hmmer -o my_catastrophy_results.csv my_fasta_hmmer.txt
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
| `-c`/`--counts` | Not written | Write the CAZyme counts to this tab delimited file. |
| `-p`/`--pca` | Not written | Write the PCA results and best scoring RCD classes to this tab separated file. This will include the training data results in the table for comparison. Useful for plotting your data.
| `-m`/`--model` | latest | The version of the model (matching the dbCAN database version) to use. The latest version is used by default. See `catastrophy -h` for list of valid options. |


Basic usage:

```bash
# To stdout aka "-o -"
catastrophy infile1.txt infile2.txt > results.csv

# To specify an output filename
catastrophy -o results.csv infile1.txt infile2.txt

# To take input from stdin use a "-"
cat infile1.txt | catastrophy - > results.csv
```
