# CATAStrophy

CATAStrophy is a classification method for describing lifestyles/trophic characteristics
of filamentous plant pathogens using carbohydrate-active enzymes (CAZymes).
The name CATAStrophy is a backronym portmanteau hybrid where "CATAS" means
CAZyme Assisted Training And Sorting.

CATAStrophy takes HMMER3 files from searches against [dbCAN](http://csbl.bmb.uga.edu/dbCAN/)
as input and returns pseudo-probabilities (See details) of trophic class memberships for each file.


## Installing

CATAStrophy is a python program which can be used as a module or via a
command-line interface.


NOTE: Because the repository currently private the following `pip` command won't work.
Use the methods to install from git instead for now.

You can install from Pypi using pip:

```bash
pip3 install --user catastrophy
```

You can also install directly from the git repository.

```bash
pip3 install --user git+git@bitbucket.org:ccdm-curtin/catastrophy.git
```

```bash
git clone https://<your_username>@bitbucket.org/ccdm-curtin/catastrophy.git ./catastrophy
cd catastrophy
pip install --user .
# Or use pip install -e . if you want to edit the modules.
```

CATAStrophy is tested to work with python 3.5+, and it depends on
[numpy](http://www.numpy.org/).
The pip commands above should install these for you automatically but if you
use any of these packages yourself it's a good idea to install CATAStrophy in
a python [virtual environment](https://virtualenv.pypa.io/en/stable/)
(You should probably use these when installing most python packages).

Using `virtualenv` is pretty easy, here's a basic rundown of the workflow.

```bash
# If it isn't installed already run one of these
# Try to use the system package managers if possible to avoid mixing up system dependencies.
sudo pip3 install virtualenv
sudo apt install python3-virtualenv # Ubuntu and probably Debian
sudo dnf install python3-virtualenv # Fedora 24+

# Change dir to where you want the env to live (usually a project dir).
cd my_project

# Create a virtualenv in a folder ./env
# python3.7 can be substituted with you version of python.
python3.7 -m venv env
```

So now the virtualenv is set up, now you can load it and install CATAStrophy

```bash
# Loads the virtualenv (essentially changes PYTHONPATH and some other env variables).
source env/bin/activate

pip3 install catastrophy
# or
pip3 install git+https://<your_username>@bitbucket.org/ccdm-curtin/catastrophy.git
# or
git clone https://<your_username>@bitbucket.org/ccdm-curtin/catastrophy.git ./
pip install .
```

## Using CATAStrophy

The command line interface is pretty simple, you just need to supply the input
files and where to put the output. The input files should be the output
from [HMMER3](http://hmmer.org/) `hmmscan` as either the raw HMMER3 text
output or the "domain table" output provided by the `--domtblout` flag.
Parsing the domain table output is about twice as fast as the regular text
output, so if you have lots of files to run it might be worth saving those files.

The easiest way to get a file like this is to annotate your proteome using
the dbCAN online tool at <http://csbl.bmb.uga.edu/dbCAN/annotate.php>, and
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


If you _really_ want to you could also mix and match stdin and filepaths using "-" to specify stdin.

```bash
cat dbcan_2.txt | catastrophy -i dbcan_1.txt - -o my_catastrophy_results.csv
```

So the second result row in the output would come from stdin.
Of course, if you cat multiple files into catastrophy they will all be treated
as a single file so it doesn't usually make sense to use stdin with multiple inputs.


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
<http://csbl.bmb.uga.edu/dbCAN/download.php> in the readme.txt file.
It isn't the most friendly documentation though so i'll repeat it here
(assuming that you've installed [HMMER](http://hmmer.org/) and are using a unix-like OS).

First download the HMMs and the parser script.

```bash
cd <a directory that you can work in>

mkdir -p ./data
wget -qc -P ./data http://csbl.bmb.uga.edu/dbCAN/download/dbCAN-fam-HMMs.txt.v5

# Optional, useful for summarising your dbCAN 
# results but not necessary for CATAStrophy.
wget -qc -P ./data http://csbl.bmb.uga.edu/dbCAN/download/hmmscan-parser.sh
```

Note that I'm downloading a specific version of the database rather that just the latest one.
Now we can convert the file containing HMM definitions into a HMMER database.

```bash
hmmpress ./data/dbCAN-fam-HMMs.txt.v5
```

Now we can run HMMER to find matches to the dbCAN HMMs.
For demonstration, we'll save both outputs.

```bash
hmmscan --domtblout my_fasta_hmmer.csv ./data/dbCAN-fam-HMMs.txt.v5 my_fasta.fasta > my_fasta_hmmer.txt
```

The domain table is now in the file `my_fasta_hmmer.csv` and the plain hmmer
text output is in `my_fasta_hmmer.txt`.
Either one of these files is appropriate for use with CATAStrophy, (just
remember to specify the `--format` flag.
In practise, you'll probably only need the domain table output in which case you
could just redirect the standard output to `/dev/null` to delete it.

If you want to look at the dbCAN matches, you can use the summary script from
dbCAN.
This script takes the domain table output from hmmscan as input and returns a new tabular file.

```bash
bash ./data/hmmscan-parser.sh my_fasta_hmmer.csv > my_fasta_dbcan.csv
```

And that's it!


# Details

Some extra details about the CATAStrophy method, including the classes used and the calculation of the RCD.
