import os
os.chdir("../")
from native.api import trip_Search
print(trip_Search('LAS', 'ATL', '2022-05-06', 'WN'))