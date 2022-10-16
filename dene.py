import pandas as pd

a = pd.read_csv("positions2.csv")
c = {"symbol": "IVIR", "side": "long",
     "entryPrice": 33400}
c = pd.DataFrame([c])
# d = a.loc[a[a["symbol"] != "SAND"]]
d = pd.concat([a, c], axis=0, ignore_index=True)
d.to_csv("positions2.csv", index=False)
print(d.loc[d["symbol"] != "SAND"])
