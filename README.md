# BibBoost: Caching Bib Files for BibTeX

BibBoost automatically extracts entries from LaTeX `aux` files and caches large `bib` files automatically into a `sqlite3` database, in order to significantly speed up the generation of the bibliography.

*Warning:* The software is an alpha software. It has only be tested on very simple LaTeX / BibTeX examples and might fail on more complex examples.

*Warning:* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED.

### Requirements

To use BibBoost from the Git sources:

- `python3` required
- packages specified in `requirements.txt`: `python3 -m pip install -r requirements.txt`
- `pypy3` optional but recommended

To use the standalone BibBoost (see the Standalone Application section):

- `python3` required
- `pypy3` optional but recommended

For development, testing, generation of the standalone version, in addition to all the above:

- `pypy3` required
- `virtualenv` required: `python3 -m pip install virtualenv`
- `bats` <https://github.com/sstephenson/bats>
- running `git submodule update --init`

### Getting Started

BibBoost can be used as a drop-in replacement for BibTex.
Instead of running

    bibtex mylatexfile.aux

you can run

    python3 bibboost.py mylatexfile.aux
    bibtex mylatexfile.aux

or

    python3 bibboost.py --run-bibtex mylatexfile.aux

or (recommended if `pypy3` is installed)

    pypy3 bibboost.py mylatexfile.aux
    bibtex mylatexfile.aux

or

    pypy3 bibboost.py --run-bibtex mylatexfile.aux
    
The first execution after any change to any `bib` file might be slow as the database `mylatexfile.bibboost.cache` needs to be created.
Subsequent executions should be much faster (assuming the number of citations in the LaTeX file is much smaller than the number of entries in the bib files).

### FAQ

#### How Does it Work?

BibBoost reads the `aux` file to find the list of `bib` files used.
The first time BibBoost is used or after any modification of the `bib` files (including the order of files, as BibTeX is sensitive to order), BibBoost parses the `bib` files and store each BibTeX entry into a `sqlite3` database `<aux file>.bibboost.cache`.
Changes of `bib` files are detected using the date of last modification.

Then, BibBoost, extracts from the `sqlite3` database the entries used in the `aux` file into the file `<aux file>.bibboost.bib`.

Finally, it modifies the the `aux` file to point to `<aux file>.bibboost.bib` instead of the original `bib` files (it also adds a special line in the `<aux file>` to remember the original `bib` files for future execution).

If the option `--run-bibtex` is given, BibBoost automatically runs `bibtex`.

#### What Should I Do with the `*.bibboost*` files?

`*.bibboost*` files are similar to `*.aux`, `*.log`, ...
These files should *not* be committed on a Git folder.

#### Nothing is Working. What Should I Do?

Start by removing all the `*.bibboost*` files.

#### Is `Biber`, `natbib`, `biblatex`, ...?

This is an early alpha software.
None of these configurations have been tested.

#### Is `nocite{*}` Supported?

No and we do not plan to support it as it completely defeats the purpose of BibBoost.

### Standalone Application

For easy distribution, it is possible to generate a standalone application by running:

    make

The resulting application is generated in `build/bibboost.pyz`.
It only requires `python3` to run correctly.
It can then be used as:

    python3 bibboost.pyz

or (recommended)

    pypy3 bibboost.pyz


### Testing

Run

    make test