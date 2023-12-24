# swap-anything

A mix and match (swap) library to empower swapping-based projects.

[![Docs](https://github.com/founderswap/swap-anything/actions/workflows/build_docs.yaml/badge.svg)](https://founderswap.github.io/swap-anything/)
[![Tests](https://github.com/founderswap/swap-anything/actions/workflows/test.yaml/badge.svg)](https://github.com/founderswap/swap-anything/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/founderswap/swap-anything/graph/badge.svg?token=QF6L5Y8EPM)](https://codecov.io/gh/founderswap/swap-anything)
[![PyPI version](https://badge.fury.io/py/swap-anything.svg)](https://badge.fury.io/py/swap-anything)

> NOTE: `swapanything` is still in its proof-of-concept phase (some
> of the things in readme are not implemented yet!). If you want to
> contribute or sponsor this project, visit
> [www.founderswap.xyz](https://www.founderswap.xyz)

## Quickstart

Check the [developer guide](./docs/about/developer-guide.md)


### Your first matching round

This library allow you to match subjects (people, things, whatever) depending
on their availability slots (calendar slots, timeframe, location,
any combination of the abovementioned). Truly, you can use this library as
backend for any sort of matching need.

The simplest way to test this library is to use the `swapanything` python
package to make a simple swapping exercise.

```python
from swapanything.backend import simple as backend
from swapanything.select import select_matches
import pandas as pd

availabilities = [
   ["KungFury", "9:00"],
   ["KungFury", "10:00"],
   ["KungFury", "13:00"],
   ["KungFury", "14:00"],
   ["Triceracop", "9:00"],
   ["Triceracop", "11:00"],
   ["Hackerman", "10:00"],
   ["Hackerman", "11:00"],
   ["Katana", "12:00"],
   ["Barbarianna", "12:00"],
   ["Thor", "13:00"],
   ["Thor", "14:00"],
   ["Thor", "15:00"],
   ["T-Rex", "15:00"],
   ["T-Rex", "16:00"],
   ["Hoff 9000", "16:00"],
]

availabilities_df = pd.DataFrame(
   availabilities, columns=["subject", "availability"]
)

be = backend.SimpleBackend(
   availabilities=availabilities_df,
   availabilities_column="availability",
   availability_subject_column="subject",
)

all_possible_matches = be.get_all_matches()
#                    subject    availability
# 0    (Barbarianna, Katana)        (12:00,)
# 1    (Hackerman, KungFury)        (10:00,)
# 2  (Hackerman, Triceracop)        (11:00,)
# 3       (Hoff 9000, T-Rex)        (16:00,)
# 4         (KungFury, Thor)  (13:00, 14:00)
# 5   (KungFury, Triceracop)         (9:00,)
# 6            (T-Rex, Thor)        (15:00,)

select_matches(all_possible_matches, backend=be)
#                    subject    availability
# 0    (Barbarianna, Katana)        (12:00,)
# 1  (Hackerman, Triceracop)        (11:00,)
# 2       (Hoff 9000, T-Rex)        (16:00,)
# 3         (KungFury, Thor)  (13:00, 14:00)

```

Imagine now that we want to provide a super high importance
to the match `(KungFury, Triceracop)`.
With `select_matches` you can use match scores, and the
algorithm will try to maximize number of matches and total
score!

This way we ensure that high wality matches are selected.

```python
scores = [1, 1, 1, 1, 1, 9001, 1]
# (KungFury, Triceracop)... it's over 9000!
select_matches(all_possible_matches, backend=be, match_scores=scores)
#                   subject availability
# 0   (Barbarianna, Katana)     (12:00,)
# 1  (KungFury, Triceracop)      (9:00,)
# 2           (T-Rex, Thor)     (15:00,)

```

### Advanced Backends

With python, it is possible to integrate `swapanything` in your application
or custom tool. `swapanything` comes with some pre-configured data backends
(e.g. Airtable, Excel Spreadsheets, SQL) that you can easily use to
kickstart your swaping-based app!

#### Airtable

Install airtable dependencies:

```shell
pip install swap-anything[airtable]
```

```python
from swapanything.backend import airtable
from swapanything.select import select_matches
import os


airtable_backend = airtable.AirTableBackend(
    # subject_id is the record id of the subjects table
    subject_features=["Interests", "Tags", "Score1", "Score2"],
    availability_subject_column="AvailabilitiesSubjectId",
    availabilities_column="Availabilities",
    exclusions_subject_columns=["Subject1", "Subject2"]
    # Tables
    subjects_table_name="Subjects",
    availabilities_table_name="Availabilities",
    exclusions_table_name="Matches",
    # Airtable credentials
    client_id=os.environ["AIRTABLE_BASE_ID"],
    client_secret=os.environ["AIRTABLE_API_KEY"],
)

subjects = airtable_backend.get_subjects()
availabilities = airtable_backend.get_availabilities()

all_matches = be.get_all_matches(exclusions=True)
selected = select_matches(matches, backend=airtable_backend)
```

### Using CLI (POC)

> This part is in proof of concept stage. Yet to be done!

You can start swapping using spreadsheets as sources/destinations of data.
Let's prepare 3 files:

1. `subjects.xlsx` - the table of subjects to match with
   details on features to use to calculate the score for a match.
   Made as follow:

   | SubjectId | Interests | Tags  | Score1 | Score2 |
   | :-------- | :-------- | :---- | -----: | -----: |
   | sub001    | i1,i2     | t1,t2 |    0.2 |    0.5 |
   | sub002    | i1        | t2    |    0.2 |    0.1 |
   | sub003    | i3        | t1    |   0.15 |    0.2 |
   | sub004    | i1,i2     | t1    |    0.2 |    0.5 |

2. `availabilities.xlsx` - a table containing match slots.
   Subjects can match when they have one or more slots in common.
   Made as follow:

   | AvailabilitiesSubjectId | Availabilities                     |
   | :---------------------- | :--------------------------------- |
   | sub001                  | 2023-01-01 15:30, 2023-01-02 16:30 |
   | sub002                  | 2023-01-01 15:30                   |
   | sub003                  | 2023-01-01 15:30                   |
   | sub004                  | 2023-01-02 16:30                   |

3. `exclusions.xlsx` - a table containing matches to exclude
   (e.g. subjects that have already matched). Made as follow:

   | Subject1 | Subject2 |
   | :------- | :------- |
   | sub001   | sub004   |

Then you can use the command line tool to make the swapping ✨

```shell
swapanything --from spreadsheet \
    --subject-id SubjectId \
    --subject-features Interests,Tags,Score1,Score2 \
    --availabilities-subject-col AvailabilitiesSubjectId \
    --availabilities-column Availabilities \
    --exclusions-subject1-id Subject1 \
    --exclusions-subject2-id Subject2 \
    --subjects subjects.xlsx \
    --availabilities availabilities.xlsx \
    --exclusions exclusions.xlsx \
    --to spreadsheet output.xlsx
```

This will result in the following `output.xlsx`, containing all new matches:

| subject1 | subject2 | slot             |
| :------- | :------- | :--------------- |
| sub001   | sub002   | 2023-01-01 15:30 |
