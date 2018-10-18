import io
import logging
import os
import sqlite3

import pybtex.database.input.bibtex
import pybtex.database.output.bibtex
import pybtex.database
from pybtex.utils import OrderedCaseInsensitiveDict


class FastWriter(pybtex.database.output.bibtex.Writer):
    """
    A version of bibtex Writer which bypass some slow operations
    knowing that the entries we are using are well-formed
    (might create bugs... not completely checked)
    """

    def _encode(self, s):
        return s  # bypass encoding, as encoding is very slow and normally we don't have issues with encoding

    def check_braces(self, s):
        return  # bypass checking braces

    def write_entry_stream(self, key, entry, stream):
        stream.write('@%s' % entry.original_type)
        stream.write('{%s' % key)
        for role, persons in entry.persons.items():
            self._write_persons(stream, persons, role)
        for type, value in entry.fields.items():
            self._write_field(stream, type, value)
        stream.write('\n}\n')

    def entry_to_string(self, key, entry):
        stream = io.StringIO() if self.unicode_io else io.BytesIO()
        self.write_entry_stream(key, entry, stream)
        return stream.getvalue()


class CacheBib:
    def _create_tables(self):
        self.con.execute("""CREATE TABLE IF NOT EXISTS bib_file (
            id INTEGER PRIMARY KEY ASC, /* must be 0,1,2,3, ... in order of inclusion */
            name TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        );""")
        self.con.execute("""CREATE TABLE IF NOT EXISTS entry (
            key TEXT NOT NULL PRIMARY KEY,
            entry TEXT NOT NULL/*,
            bib_file_id INTEGER NOT NULL,
            FOREIGN KEY(bib_file_id) REFERENCES bib_file(id) ON DELETE CASCADE */
        );""")
        self.con.commit()

    def __init__(self, filename):
        self.con = sqlite3.connect(filename)
        self._create_tables()

        self.bibtex_writer = FastWriter()

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        self.close()

    def close(self):
        self.con.close()

    def is_db_up_to_date(self, bib_files):
        """
        Check whether the database contains exactly the current bib_files
        :param bib_files:
        :return:
        """

        t = [
            (i, name, os.path.getmtime(name))
            for i, name in enumerate(bib_files)
        ]
        return self.con.execute("""SELECT id, name, `timestamp` FROM bib_file;""").fetchall() == t

    def update_db(self, bib_files):
        """
        Update the database to match the bib_files
        If name/order/timestamp do not match, the database is re-created
        :param bib_files: ordered list of bibtex files
        :return:
        """

        if self.is_db_up_to_date(bib_files):
            logging.info("SQL cache database up to date")
            return

        logging.info("SQL cache database out of date. Recreating it...")

        # Remove everything
        self.con.execute("DROP TABLE bib_file;")
        self.con.execute("DROP TABLE entry;")
        self._create_tables()

        # and add back files and entries
        self.add_bib_files_with_entries(bib_files)
        self.con.commit()

    def get_entries(self, keys):
        """

        :param keys:
        :return: an array of tuple (key, entry) of found entries
        """

        return self.con.execute(
            """SELECT `key`, `entry` FROM entry WHERE `key` in ({})""".format(",".join(["?"] * len(keys))), keys
        ).fetchall()

    def gen_entry_bibtex(self, key, entry):
        """
        Return the bibtex corresponding to an entry
        :param entry:
        :return:
        """

        return self.bibtex_writer.entry_to_string(key, entry)

    def add_bib_files_with_entries(self, bib_files):
        """

        Does not commit the transaction
        :param bib_files:
        :return:
        """

        # person_fields = [] so that pybtex does not try parsing persons
        bib_parser = pybtex.database.input.bibtex.Parser(person_fields=[])
        bib_data = None
        for (i, bib_file) in enumerate(bib_files):
            self.add_bib_file(i, bib_file)
            bib_data = bib_parser.parse_file(bib_file)

        entries = [(key, self.gen_entry_bibtex(key, entry)) for key, entry in bib_data.entries.items()]

        self.add_entries(entries)

    def add_bib_file(self, bib_file_id, file_name):
        """
        Does not add entries
        Does not commit the transaction
        Does not add the corresponding entries
        :param bib_file_id:
        :param file_name:
        :return:
        """
        timestamp = os.path.getmtime(file_name)
        self.con.execute("""INSERT INTO bib_file (
            id,
            name,
            `timestamp`
        )
        VALUES (
            ?,
            ?,
            ?
        );
        """,
                         (bib_file_id, file_name, timestamp))

    def add_entries(self, entries):
        """
        Throws an error if an entry is already present.
        Does not commit the transaction.
        :param entries: list of pairs (key, entry), where entry is a Bibtex string
        :return:
        """
        self.con.executemany("""INSERT INTO entry (
                key,
                entry
            )
            VALUES (
                ?,
                ?
            );                 
            """,
                             entries)
