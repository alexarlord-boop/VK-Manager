from requests import get, delete
from flask import jsonify
import json
# PAGES

# print(delete('http://localhost:5000/api/v1/pages/166469585').json())

x, y = list(map(int, input().split()))

for i in range(1, 9):
    for j in range(1, 9):
        d1 = abs(x - j)
        d2 = abs(y - i)

        if ((d1==1) and (d2==2)) or ((d1==2) and (d2==1)):
            print(j, i)


# PUBLICS
# print(get('http://localhost:5000/api/v1/pages/publics/all').json())
# print(get('http://localhost:5000/api/v1/pages/publics/166469585').json())
# print(delete('http://localhost:5000/api/v1/pages/publics/166469585').json())

# GROUPS
# print(get('http://localhost:5000/api/v1/pages/groups/all').json())

# EVENTS
# print(get('http://localhost:5000/api/v1/pages/events/all').json())
