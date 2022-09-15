from sklearn import datasets
from sklearn.linear_model import LinearRegression
# from sklearn.
# from snowflake.snowpark.functions import col

def model(dbt, session):

    dbt.config(
        materialized="table",
        packages=['sklearn']
    )

    # split dataset / get data
    # will import model, then unbundle X & y
    diabetes_X, diabetes_y = datasets.load_diabetes(return_X_y=True, as_frame=True)
    X_train, X_test, y_train, y_test = train_test_split(diabetes_X, diabetes_y, test_size=0.33, random_state=42)

    # fit predictor
    # how can we save / use this
    model = LinearRegression().fit(X_train, y_train)

    # get predictions - new model
    predictions = model.predict(y_test)

    return model