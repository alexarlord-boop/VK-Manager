from requests import get
import json

# PUBLICS
# print(get('http://localhost:5000/api/v1/pages/publics/all').json())
# print(get('http://localhost:5000/api/v1/pages/publics/166433904').json())

# GROUPS
print(get('http://localhost:5000/api/v1/pages/groups/all').json())

# EVENTS
# print(get('http://localhost:5000/api/v1/pages/events/all').json())
