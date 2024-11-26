import re
from xxlimited_35 import error

patter = 'Ключ \(recipe_id\)=\(\d+\) отсутствует в таблице "recipe"'
input_error = '  Ключ (recipe_id)=(1) отсутствует в таблице "recipe".'
# print(input_error)
if re.findall(patter, input_error):
    print(True)
else:
    print(False)
