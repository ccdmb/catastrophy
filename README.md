# CATAStrophy

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
If a new proteome is equidistant between two class centroids, both RCD scores will be one, so the RCD method is a _kind_ of multi-label classifier.
This is useful when evaluating your organism, because it might have characteristics of multiple classes (or be so dissimilar to any class that the distance is meaningless).


## Installing

CATAStrophy is a python program which can be used as a python module or via a command-line interface.

It is tested to work with python 3.6+, and it depends on [numpy](http://www.numpy.org/) and [BioPython](https://biopython.org/).
The install procedures below will install these for you automatically.

CATAStrophy can be installed from Pypi <https://pypi.org/project/catastrophy/> using [pip](https://pip.pypa.io/en/stable/).

Installing with pip:

```bash
python3 -m pip install --user catastrophy
```

The `--user` flag tells pip to install to a user directory rather than a system directory (e.g. somewhere under `/usr/` or `Program Files`).
To install as root or in Windows you can omit the `--user` flag, but you may need root/administrator permission.

Note that the `--user` subdirectory containing scripts (`<userdir>/bin` on linux/mac or `<userdir>\Scripts` on Windows), may not automatically be on your path.
The user directory installed to is given by the python command `import site; print(site.USER_BASE)`.
Generally on linux this is `~/.local`.
You can change this directory by setting the `$PYTHONUSERBASE` environment variable.
You can then add the `Script` or `bin` subdirectory to your `$PATH` environment variable 
(e.g. [Linux and MacOS](https://stackoverflow.com/questions/14637979/how-to-permanently-set-path-on-linux-unix), or [Windows](https://stackoverflow.com/questions/9546324/adding-directory-to-path-environment-variable-in-windows), or just google it ;) ).

Power users may also be interested in the `pip install --prefix` flag, but this will also require you to update your `$PYTHONPATH` environment variable.
Nonetheless, it's useful for [module](http://modules.sourceforge.net/) software management.

You can also install directly from the git repository to get the latest and greatest.
We use [git-lfs](https://git-lfs.github.com/) to handle some filetypes, so you'll need to install that first.

```bash
python3 -m pip install --user git+git@bitbucket.org:ccdm-curtin/catastrophy.git
```

```bash
git clone https://<your_username>@bitbucket.org/ccdm-curtin/catastrophy.git ./catastrophy
cd catastrophy
python3 -m pip install --user .
# Or use pip install -e . if you want to edit the modules.
```

If you use numpy or biopython yourself it's a good idea to install CATAStrophy in a python [virtual environment](https://virtualenv.pypa.io/en/stable/)
(You should probably use these when installing most python packages).

Using `virtualenv` is pretty easy, here's a basic rundown of the workflow.

```bash
# If it isn't installed already run one of these
# Try to use the system package managers if possible to avoid mixing up system dependencies.
sudo python3 -m pip install virtualenv
sudo apt install python3-virtualenv # Ubuntu and probably Debian
sudo dnf install python3-virtualenv # Fedora 24+

# Change dir to where you want the env to live (usually a project dir).
cd my_project

# Create a virtualenv in a folder ./env
# python3 can be substituted with your version of python.
python3 -m venv env

# Loads the virtualenv (essentially changes PYTHONPATH and some other env variables).
source env/bin/activate
```

So now the virtualenv is set up, now you can install CATAStrophy as before using pip.
Note however that you'll need to repeat the `source` command if you start a new terminal.


## Using CATAStrophy

The to run CATAStrophy you need to supply the input
files and where to put the output.
The input files should be the output from [HMMER3](http://hmmer.org/) `hmmscan` as either the raw HMMER3 text
output or the "domain table" output provided by the `--domtblout` flag.
Parsing the domain table output is about twice as fast as the regular text
output, so if you have lots of files to run it might be worth saving those files.

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
The `-f/--format` flag is optional and defaults to `hmmer`, but if you want to
use domain table output, you should include the flag `-f domtab` (run
`catastropy --help` for more options).

NOTE: In this document I use the `.csv` extension to mean any plain text tabular
format because excel doesn't recognise alternate extensions like `.tsv`.
The domain table output is actually space delimited and the catastrophy
output is a tab delimited file.

By default the filenames are used as the label but you can explicitly specify
a label using the `-l/--label` flag. The output from the command above will
have two lines, one containing the column headers and the other containing
results for the file `my_dbcan_results.txt` which will have the label
"my_dbcan_results.txt".

To give it a nicer label you can run this.

```bash
catastrophy -i my_dbcan_results.txt -l prettier_label -o my_catastrophy_results.csv
```

Which would give the output line for `my_dbcan_results.txt` the label "prettier_label".
Unfortunately, labels cannot contain spaces unless you explicitly escape them (quotes won't work).

If you want to run multiple files at the same time you just need to separate the files by spaces, like this:

```bash
catastrophy -i dbcan_1.txt dbcan_2.txt -o my_catastrophy_results.csv

# Or equivalently
catastrophy -i dbcan_*.txt -o my_catastrophy_results.csv
```

The output from this will contain three rows, one containing the headers and
the other two containing the results for the files `dbcan_1.txt` and `dbcan_2.txt`
which will be labelled by the filenames.
Note that standard bash "globbing" patterns expand into a space delimited array,
so you can easily use "*" or subshells if you like (eg. `$(find . -type f -name *.txt)` etc).
To explicitly label these files you can again supply the label flag with the space separated labels.

```bash
catastrophy -i dbcan_1.txt dbcan_2.txt -l label1 label2 -o my_catastrophy_results.csv
```

Note that if you do use the label flag, the number of labels **must** be the same as the number of input files.

Both the input and output flags support standard input/output (they are actually the default values).
So you could change the single file commands from above to:

```bash
cat my_dbcan_results.txt | catastrophy -l prettier_label > my_catastrophy_results.csv

# or using the convention for "-" representing stdin/stdout

cat my_dbcan_results.txt | catastrophy -i - -l prettier_label -o - > my_catastrophy_results.csv
```

If you don't spefify a label for stdin input the label will be "<stdin>".


Finally because dbCAN is updated as new CAZyme classes are created, merged,
or split, catastrophy has a final parameter that allows you to select the
model trained on a specific dbCAN version (starting from version 5).

To specify the version of the model to use, just include the `-m/--model`
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
remember to specify the `--format` flag.

```bash
catastrophy -m v7 -i my_fasta_hmmer.csv --format domtab -o my_catastrophy_results.csv

# or
catastrophy -m v7 -i my_fasta_hmmer.txt --format hmmer -o my_catastrophy_results.csv
```

And that's it!


# What does CATAStrophy do?

CATAStrophy performs principle components analysis (PCA) on the frequencies of carbohydrate active enzymes (CAZymes) in your sample.
It then compares the position of 

The predictions from CATAStrophy are based on the "relative centroid distance".


Some extra details about the CATAStrophy method, including the classes used and the calculation of the RCD.
