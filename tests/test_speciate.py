# -*- coding: utf-8 -*-
"""Tests for speciation module."""

import pkg_resources
import os
from finnemit import speciate


def test_csv_output(tmpdir):
    infile = pkg_resources.resource_filename("finnemit",
                                             "data/example-output.csv")
    outfile = os.path.join(str(tmpdir), "out.csv")
    speciate(infile, outfile)
    assert os.path.isfile(outfile)


def test_logfile_output(tmpdir):
    infile = pkg_resources.resource_filename("finnemit",
                                             "data/example-output.csv")
    outfile = os.path.join(str(tmpdir), "out.csv")
    logfile = os.path.join(str(tmpdir), "out_log.txt")
    speciate(infile, outfile)
    assert os.path.isfile(logfile)
