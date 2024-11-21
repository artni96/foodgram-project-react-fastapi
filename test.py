import re

if not re.match(r'^[\w-]+@([\w-]+\.)+[\w-]{2,4}$', '12-34@aw.ru'):
    print(False)
else:
    print(True)
