# Getting Started


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

This way we ensure that high quality matches are selected.

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
