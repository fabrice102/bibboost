#!/usr/bin/env bats

clean() {
    make clean
}

setup() {
    clean
}

teardown() {
    clean
}

load 'test_helper/bats-support/load'
load 'test_helper/bats-assert/load'

@test "bibtex_micro" {
    FILE=bibtex_micro

    run pdflatex $FILE.tex
    assert_success

    run python3 ../bibboost.py $FILE.aux
    assert_success
    assert_line 'bibboost:INFO:SQL cache database out of date. Recreating it...'

    run python3 ../bibboost.py $FILE
    assert_success
    assert_line 'bibboost:INFO:SQL cache database up to date'

    bibtex $FILE
    assert_success

    run pdflatex $FILE.tex
    assert_success
}

@test "bibtex_micro --run-bibtex" {
    FILE=bibtex_micro

    run pdflatex $FILE.tex
    assert_success

    run python3 ../bibboost.py --run-bibtex $FILE.aux
    assert_success
    assert_line 'bibboost:INFO:SQL cache database out of date. Recreating it...'

    run python3 ../bibboost.py $FILE
    assert_success
    assert_line 'bibboost:INFO:SQL cache database up to date'

    run pdflatex $FILE.tex
    assert_success
}

@test "bibtex_micro_missing" {
    FILE=bibtex_micro_missing

    run pdflatex $FILE.tex
    assert_success

    run python3 ../bibboost.py $FILE
    assert_success
    assert_line 'bibboost:INFO:SQL cache database out of date. Recreating it...'
    assert_line 'bibboost:WARNING:missing entries: missing'

    run python3 ../bibboost.py $FILE
    assert_success
    assert_line 'bibboost:INFO:SQL cache database up to date'
    assert_line 'bibboost:WARNING:missing entries: missing'

    bibtex $FILE
    assert_success

    run pdflatex $FILE.tex
    assert_success
}

@test "bibtex_large" {
    FILE=bibtex_large

    run pdflatex $FILE.tex
    assert_success

    run python3 ../bibboost.py $FILE.aux
    assert_success
    assert_line 'bibboost:INFO:SQL cache database out of date. Recreating it...'

    run python3 ../bibboost.py $FILE
    assert_success
    assert_line 'bibboost:INFO:SQL cache database up to date'

    bibtex $FILE
    assert_success

    run pdflatex $FILE.tex
    assert_success
}

@test "bibtex_micro pypy3 (requires pypy3 installed)" {
    FILE=bibtex_micro

    run pdflatex $FILE.tex
    assert_success

    run pypy3 ../bibboost.py --run-bibtex $FILE.aux
    assert_success
    assert_line 'bibboost:INFO:SQL cache database out of date. Recreating it...'

    run pypy3 ../bibboost.py $FILE
    assert_success
    assert_line 'bibboost:INFO:SQL cache database up to date'

    run pdflatex $FILE.tex
    assert_success
}