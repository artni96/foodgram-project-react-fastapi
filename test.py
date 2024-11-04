import re

test_string = 'test123_фывф'

pattern = '^[-a-zA-Z0-9_]+$'

if re.fullmatch(pattern=pattern, string=test_string):
    print(True)
