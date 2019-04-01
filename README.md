FINN Emitter
============

[![Build Status](https://travis-ci.org/mbjoseph/finnemit.svg?branch=master)](https://travis-ci.org/mbjoseph/finnemit)
[![codecov](https://codecov.io/gh/mbjoseph/finnemit/branch/master/graph/badge.svg)](https://codecov.io/gh/mbjoseph/finnemit)



Emissions estimates for the Fire Inventory (FINN) wildfire emissions model (Wiedinmyer et al. 2011).
This library ingests a comma separated values (CSV) file generated from the FINN
pre-processor (https://github.com/yosukefk/finn_preproc), and generates a
CSV file with estimated emissions for a variety of compounds.

## Installation

Assuming you have python and pip installed:

```bash
pip install git+https://github.com/mbjoseph/finnemit
```

## Usage

The main function in the finnemit library is `get_emissions`, which takes
as input a path to a CSV file generated using the FINN preprocessor, and
an output path.
In python:


```python
import finnemit

finnemit.get_emissions(infile = 'path/to/in.csv', outfile='path/to/out.csv')
```

If the `outfile` argument is not specified, an output filename will be
automatically generated and saved in the same directory as the input file.


## Meta

* Free software: BSD license

This package was created with Cookiecutter_ and the pyOpenSci/cookiecutter-pyopensci project template.

* Cookiecutter: https://github.com/audreyr/cookiecutter
* pyOpenSci/cookiecutter-pyopensci: https://github.com/pyOpenSci/cookiecutter-pyopensci
* audreyr/cookiecutter-pypackage: https://github.com/audreyr/cookiecutter-pypackage

For more information on FINN, see:

Wiedinmyer, Christine, et al. "The Fire INventory from NCAR (FINN): A high
resolution global model to estimate the emissions from open burning."
Geoscientific Model Development 4.3 (2011): 625. 10.5194/gmd-4-625-2011
