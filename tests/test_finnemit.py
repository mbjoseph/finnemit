# -*- coding: utf-8 -*-
"""Tests for `finnemit` package."""

import pkg_resources
import os
from finnemit import get_emissions


def test_csv_output(tmpdir):
    infile = pkg_resources.resource_filename("finnemit", "data/example-input.csv")
    outfile = os.path.join(str(tmpdir), "out.csv")
    get_emissions(infile, outfile)
    assert os.path.isfile(outfile)


def test_dict_returned(tmpdir):
    infile = pkg_resources.resource_filename("finnemit", "data/example-input.csv")
    outfile = os.path.join(str(tmpdir), "out.csv")
    assert isinstance(get_emissions(infile, outfile), dict)
