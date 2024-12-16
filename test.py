class Person:
    # __slots__ = ['age', 'name']
    def __init__(self, age, name):
        self.name = name
        self.age = age

vanya = Person(name='Vanya', age=26)
print(dir(vanya))
