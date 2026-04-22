# CtP Share Table Construction

This repository contains the implementation of the Cover-then-Patch (CtP) share-table construction for $(t,n)$ threshold secret sharing.

## Overview

The code implements:

* The CtP layout generation (cover and patch phases)
* Construction of the public share-table schema
* Share count statistics for each party

The implementation follows the construction described in the paper and allows reproducible evaluation of structural properties.

---

## Files

* `ctp.py`
  Core implementation of the CtP construction, including layout generation and share-table schema.

* `experiment.py`
  Extended version with additional functionality for computing share counts and evaluating storage overhead.

---

## Requirements

* Python 3.6 or higher
* No external dependencies required (standard library only)

---

## Usage

### Basic example (small instance)

```bash
python ctp.py --n 6 --t 3
```

This will output:

* CtP layout (cover and patch columns)
* Public share-table schema

---

### Extended experiment (recommended)

```bash
python experiment.py --n 29 --t 25
```

This will output:

* Total number of columns
* Number of cover and patch columns
* Share count per party

---

### Optional arguments

```bash
--show-table        # print full share table (only for small n)
--show-party Pk     # show shares held by a specific party (e.g., P3)
```

Example:

```bash
python experiment.py --n 6 --t 3 --show-table
python experiment.py --n 29 --t 25 --show-party P1
```

---

## Reproducibility

All results reported in the paper can be reproduced using the provided scripts.

---

## Notes

* The full share table can be very large when $n$ is large; use `--show-table` only for small instances.
* The implementation is deterministic and follows lexicographic ordering for combinations.
