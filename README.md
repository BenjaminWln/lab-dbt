## Bronze layer

**Why keep the bronze CSV files unchanged?**

If a transformation has a bug, we can fix it and rebuild the silver data from the original files. The raw data is still available, so we do not lose information.

**Which format and layout would you choose for orders received every hour for years?**

I would use compressed Parquet files, split into columns and organised by date or hour. This lets queries read only the needed columns and time periods. The files should also be combined from time to time to avoid having too many small files.

## Build

**What happens when a view is queried, and when is it better than a table?**

A view stores a SQL query, not the result. The query runs each time the view is used. A view is a good choice when the data changes often or the query is simple. A table is better when the result is used often or takes a long time to calculate.

**How many bytes does the `VARCHAR` form of a UUID use?**

A UUID written as text uses 36 bytes: 32 letters or numbers and 4 hyphens. The UUID itself uses 16 bytes.

## Data tests

**Which strategy would you choose for a customer-age dashboard and a sales-by-region dashboard?**

For the age dashboard, replace invalid birthdates with `NULL` or leave those customers out of the age calculation. Keep a flag to show which birthdates are invalid. For the sales dashboard, keep the valid sales and show a warning about the birthdate problem.

**Which test can find a state and ZIP code that do not match, and what reference data does it need?**

A test should check that each ZIP code belongs to its state. It needs a list of valid ZIP-code ranges or mappings for each state.

## Parquet export

**How do the exported Parquet file and the `stg_orders` view compare?**

They contain the same rows: both difference checks return zero rows. The view runs the query on the source each time. The Parquet file stores the result, so it may be quicker to read, but it must be exported again when the source data changes.

## Exercises

### 1. Clean username

`stg_users` has a `username_normalized` column. It removes spaces at the start and end, and changes the username to lowercase. Tests check that the value is present and correctly formatted.

### 2. Check orders

Tests check that `quantity` is positive, `product` is in the expected list, and every `user_id` exists in `stg_users`.

### 3. Check birthdates

`stg_users` has a `birthdate_is_valid` column. It is `false` when a birthdate is later than the user's first order. Invalid birthdates are changed to `NULL`. The `assert_orders_after_user_birth` test then passes.

### 4. Check ZIP codes

The `state_zip_ranges` seed contains ZIP-code ranges for each state. The `assert_state_zip_consistent` test finds users whose state and ZIP code do not match. The ranges are approximate and should be checked against a reliable source. A seed is suitable for this small reference list. The check is a test on the silver data, so it reports problems without removing user records. If the reference data changes, update the seed and run the test again.

### 5. Compare views and tables

With `+materialized: table`, dbt stores the silver rows in the DuckDB database when it builds the models. A view stores only the query and runs it each time it is used.

- A table uses more storage because it contains the result; a view stores only its query.
- A view can show changes in the source on the next query. A table must be rebuilt to include them.
- A table avoids reading the source files for every query. A view reads them when it is queried.
- The original view setting is restored after the comparison.
