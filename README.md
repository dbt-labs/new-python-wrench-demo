# the trusty Python wrench

It's without question that us dbters [stan](https://www.urbandictionary.com/define.php?term=Stan) for SQL. However, we're not zealots -- sometimes Python is exactly the way to get things done.

This dbt project shows a trivial example fuzzy string matching in Snowflake using dbt-snowflake Python models in Snowpark. [thefuzz](https://github.com/seatgeek/thefuzz) is the defacto package. While Snowflake SQL has the `EDITDISTANCE()` ([docs](https://docs.snowflake.com/en/sql-reference/functions/editdistance.html)) function, what we're after is "give me the best match for this string, as long as it's 'close enough'"

This is easily accomplished with `process.extractOne()` ([source](https://github.com/seatgeek/thefuzz/blob/791c0bd18c77b4d9911f234c70808dbf24f74152/thefuzz/process.py#L200-L225))


## Imaginiary Scenario

### Shut up and show me the code!

- [fuzzer.ipynb](fuzzer.ipynb): A notebook that shows you the code on your local machine 
- [/models/fruit_join.py](/models/fruit_join.py): A notebook that shows you the code on your local machine 

### Background

Imagine you work at a company that makes a fruit ordering app. However, rather than using a drop-down menu to select  the desired fruit, the app devs just put a text box. It's your job to tell the finance department how much each user owes.

### Process

We have two `.csv` seed tables serve as our trivial data source:

- `fruit_prices_fact.csv`: a mapping of fruits to their corresponding price
- `fruit_user_input.csv`: a table with one row per user per fruit that includes the user-entered text and their desired quantity

The resulting Python model is a table that gives the total amount due for each user. This is accomplished in the following steps

1. Get pandas DataFrames of each of the above tables
2. Find the actual fruit name that best corresponds to the user-provided text (`fruit_name`).
3. Uses new column to join to the `fruit_prices_fact` table to get the fruit price.
4. Calculates the subtotal price for each row (i.e. `total = price * quantity`).
5. Returns the total price per user


If we wanted to minimize the amount of Python and increase the testing surface area, perhaps we'd want to only use Python to do steps 1 & 2, then use a downstream SQL model to do steps 3-5. One benefit would be that we could then set a warning and error threshold if a designated perfentage of user-entered strings do not have a suitable match in the price table.

### Implementation Details

#### `thefuzz`'s `extractOne()`

[example from `thefuzz`'s README](https://github.com/seatgeek/thefuzz#process)

We make this function so that it is more easily [applied](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.apply.html) to an entire column at once.

```py
def custom_scorer(string, score_cutoff=60):
    '''
    for a given string and a minimum
    return the best match out of the `fruit_name` column in the df_to table
    if no match above `score_cutoff`, return `None`
    '''
    
    x = process.extractOne(string,df_price["FRUIT_NAME"], score_cutoff=score_cutoff)
    
    if x is not None:
        return x[0]
    else:
        return None
```


#### Pandas method chain

I'm a big fan of [Pandas method chaining](https://www.loom.com/share/31ab8e5f1018492c800d52a743ac98ee). Sometimes it makes the syntax awkward at times (I'm looking at you `.assign(fruit_name = lambda df: df['fruit_user_input'].apply(custom_scorer))`), but at least there's a series of transformation applied to a single object and you're less likely to have many copies of the dataframe all with slightly different variable names. Below is the chain in use, with comments explaining what is being done.

```py
df_final = (df_input
           # make new col, `fruit_name`, with best match against actual table
           .assign(fruit_name = lambda df: df['fruit_user_input'].apply(custom_scorer))
           # join the actual fruit price table
           .merge(df_price, on="fruit_name")
           # # calculate subtotal
           .assign(total= lambda df: df.quantity * df.cost)
           # # find total for each user and sort descending by total price
           .groupby("user_name")['total'].sum()
           .reset_index()
           .sort_values("total", ascending=False)
          )
```

#### Syntactic Sugar to make it work in Snowpark

1. make sure you configure column quoting so you can keep the lowercase column names by adding the following to your `dbt_project.yml`. Otherwise, you may get tripped up when in Snowpark and the DataFrame column names are capitalized. 
    ```yaml
    seeds:
        +quote_columns: true
    ```
2. We can inject the above snippets into the following already configured template and save it as `models/fruit_join.py`

    ```py
    # models/fruit_join.py

    import fuzzywuzzy

    def model(dbt, session):
        dbt.config(
            materialized="table",
            packages = ["fuzzywuzzy"]
            )

        df_input = dbt.ref("user_input").to_pandas()

        df_price = dbt.ref("fruit_fact").to_pandas()

        # ... see the above two chunks ...
        def custom_scorer() ...
        df_final = ...

        return df_final
    ```
3. to run this DAG, simply call `dbt build`!