# import re
# from xxlimited_35 import error
#
# patter = 'Ключ \(recipe_id\)=\(\d+\) отсутствует в таблице "recipe"'
# input_error = '  Ключ (recipe_id)=(1) отсутствует в таблице "recipe".'
# # print(input_error)
# if re.findall(patter, input_error):
#     print(True)
# else:
#     print(False)
import base64

file_name = 'xHYkxaysDq.png'

with open(f'src/media/recipes/images/{file_name}', "rb") as image_file:
    encoded_string = base64.urlsafe_b64encode(image_file.read())
    result = f'data:image/{file_name.split(".")[1]};base64,'+ encoded_string.decode('utf-8')
    print(result)
