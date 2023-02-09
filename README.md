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

## relation to the activity-browser
- original objects and functions from the ab are in the sub-modules bwutils and superstructure
- each file has the original filename as in the AB
- in the header of the file, the relative path for that file within the ab is given
- each function or objects states the source of the ab and whether it has been adapted or not. 
- all of the objects are original, unless otherwise stated, apart from the functions in the superstructure.manager, which defines functions which originally where methods of the class SuperstructureManager of the ab
- used ab version: branch: activity-browser-dev; version: 2022.11.16
- search for "Note: source" to see all objects from the activity-browser
- search for "adaptations:" to see the adaptations. no adaptations are mentioned, no adaptations were done

## License

`bw-superstructure` is distributed under the terms of the [LGPL-3.0](https://spdx.org/licenses/LGPL-3.0) license.
