class Person:
    __slots__ = ['age', 'name', 'occupation']
    def __init__(self, age, name, occupation):
        self.name = name
        self.age = age
        self.occupation = occupation

vanya = Person(name='Vanya', age=26)
print(dir(vanya))
vanya.occupation('Работник')
print(vanya)
