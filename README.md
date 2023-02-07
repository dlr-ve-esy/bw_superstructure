# bw_superstructure

[![PyPI - Version](https://img.shields.io/pypi/v/bw-superstructure.svg)](https://pypi.org/project/bw-superstructure)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/bw-superstructure.svg)](https://pypi.org/project/bw-superstructure)

-----

**Table of Contents**

- [Installation](#installation)
- [License](#license)

## Installation

```console
pip install bw-superstructure
```

## Working features
- relinking a DB to another DB
- creating a user-defined calculation set-up for several functional units and impact categories 
- calculating scenario LCA scores with a superstructure and a scenario-difference-file
- exporting the LCA scores for the scenarios for each functional unit to an excel workbook

### requirements
- a working BW2-project with databases
- functional units specified in an excel file (see inputs in example)
- impact categories specified in a yaml file (see inputs in example)
- a scenario difference file in excel (same format as for the AB)


## features missing so far
- contribution analyses
- monte carlo analysis
- combining several scenario difference files


## License

`bw-superstructure` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
