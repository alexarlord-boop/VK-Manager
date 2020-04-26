from requests import get, delete
from flask import jsonify
import json
# PAGES

# print(delete('http://localhost:5000/api/v1/pages/166469585').json())


# PUBLICS
# print(get('http://localhost:5000/api/v1/pages/publics/all').json())
# print(get('http://localhost:5000/api/v1/pages/publics/166469585').json())
# print(delete('http://localhost:5000/api/v1/pages/publics/166469585').json())

# GROUPS
# print(get('http://localhost:5000/api/v1/pages/groups/all').json())

# EVENTS
print(get('http://localhost:5000/api/v1/pages/events/all').json())
