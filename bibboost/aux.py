import re
import fileinput


def get_canonical_bib_file(name: str) -> str:
    name = name.strip()
    if not name.endswith(".bib"):
        name += ".bib"
    return name


_citation_re = re.compile(r"^\\citation\{(?P<key>[^\}]+)\}$")
_bib_files_re = re.compile(r"^\\bibdata\{(?P<files>[^}]+)\}$")
_bibboost_bib_files_re = re.compile(r"^%\\bibboostdata\{(?P<files>[^}]+)\}$")


def parse_aux_file(aux_file_name):
    with open(aux_file_name) as f:
        citations = []
        bib_files = []
        bibboost = False # True, if bibboost was actually used

        for line in f:
            p = _citation_re.match(line)
            if p is not None:
                citations.append(p.group("key"))
                continue

            p = _bibboost_bib_files_re.match(line)
            if p is not None:
                if bib_files:
                    raise ValueError("\\bibboostdata present twice in aux file or present after \\bibdata.")
                bib_files = p.group("files").split(",")
                bibboost = True

            p = _bib_files_re.match(line)
            if (p is not None) and not bibboost:
                if bib_files:
                    raise ValueError("\\bibdata present twice in aux file. bibboost only supports one \\bibdata.")
                bib_files = p.group("files").split(",")

        bib_files = [get_canonical_bib_file(name) for name in bib_files]

        return bib_files, citations


def change_bib_file(aux_file_name, bib_file_name):
    """
    Change the bib files used in `aux_file_name` into `bib_file_name`
    and replace the line `\bibdata` into `%\bibboostdata`
    :param aux_file_name:
    :param bib_file_name:
    :return:
    """
    with fileinput.FileInput(aux_file_name, inplace=True) as f:
        bibboost = False
        for line in f:
            p = _bibboost_bib_files_re.match(line)
            if p is not None:
                bibboost = True

            p = _bib_files_re.match(line)
            if p is not None:
                if not bibboost:
                    print(line.replace("\\bibdata", "%\\bibboostdata"), end="")
                print("\\bibdata{{{}}}".format(bib_file_name))
            else:
                print(line, end="")