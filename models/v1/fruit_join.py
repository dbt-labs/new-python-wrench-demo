from fuzzywuzzy import process


def model(dbt, session):
    dbt.config(
        materialized="table",
        packages=["fuzzywuzzy"]
    )

    df_input = dbt.ref("fruit_user_input").to_pandas()

    df_price = dbt.ref("fruit_prices_fact").to_pandas()

    def custom_scorer(string):
        '''
        for a given string
        return the best match out of the `fruit_name` column in the df_to table
        '''

        x = process.extractOne(string, df_price["fruit_name"], score_cutoff=60)

        if x is not None:
            return x[0]
        else:
            return None

    df_final = (df_input
                # make new col, `fruit_name`, with best match against actual table
                .assign(fruit_name=lambda df: df["fruit_user_input"].apply(custom_scorer))
                # join the actual fruit price table
                .merge(df_price, on="fruit_name")
                # calculate subtotal
                .assign(total=lambda df: df.quantity * df.cost)
                # find total for each user
                .groupby("user_name")["total"].sum()
                .reset_index()
                .sort_values("total", ascending=False)
                )

    return df_final
