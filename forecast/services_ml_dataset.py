#################################
# forecast/services_ml_dataset.py
#################################


def build_dataset(readings, weather):
    X, y = [], []

    for i in range(3, len(readings)):
        row = [
            weather[i]["radiation"],
            weather[i]["temperature"],
            weather[i]["cloudcover"],
            readings[i - 1],
            readings[i - 2],
            readings[i - 3],
        ]

        X.append(row)
        y.append(readings[i])

    return X, y
