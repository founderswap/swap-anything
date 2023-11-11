# swap-anything

A mix and match (swap) library to empower swapping-based projects.

[![Docs](https://github.com/founderswap/swap-anything/actions/workflows/build_docs.yaml/badge.svg)](https://founderswap.github.io/swap-anything/)
[![Tests](https://github.com/founderswap/swap-anything/actions/workflows/test.yaml/badge.svg)](https://github.com/founderswap/swap-anything/actions/workflows/test.yaml)
[![codecov](https://codecov.io/gh/founderswap/swap-anything/graph/badge.svg?token=QF6L5Y8EPM)](https://codecov.io/gh/founderswap/swap-anything)

> NOTE: `swapanything` is still in its proof-of-concept phase (some
> of the things in readme are not implemented yet!). If you want to
> contribute or sponsor this project, visit
> [www.founderswap.xyz](https://www.founderswap.xyz)

## Quickstart

Check the [developer guide](./docs/about/developer-guide.md)

### Using CLI (example)

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

### Using the Python API

With python, it is possible to integrate `swapanything` in your application
or custom tool. `swapanything` comes with some pre-configured data backends
(e.g. Airtable, Excel Spreadsheets, SQL) that you can easily use to
kickstart your swaping-based app!

```python
from swapanything.backend import airtable as be
from swapanything import Scorer, Selector, Swapper
import os


data_backend = be.AirTableBackend(
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

match_scorer = Scorer(model="simple")
selector = Selector(relevance_weight=.5, total_number_weight=.5)
model = Swapper(scorer=match_scorer, selector=selector)

exclusions = data_backend.get_exclusions()
all_possible_matches = data_backend.get_matches(exclusions=exclusions)
subjects = data_backend.get_subjects()

match_scores = model.score(all_possible_matches, subjects)
matches = model.select(match_scores)

```
