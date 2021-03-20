class Car():
    def __init__(self):
        self.x = 0
        self.__y = 1
    
    def return_y(self):
        return self.__y


audi = Car()

print(audi.return_y())
print(vars(audi))
print(vars(audi)["_Car__y"])
print(audi._Car__y)
audi._Car__y = "hola"
print(vars(audi))
vars(audi)["_Car__y"] = "adeu"
print(vars(audi))

for el in vars(str):
    print(el)


# print("x", audi.x)
# try:
#     audi.x = 1
#     print("x was modified:", audi.x)
# except:
#     print("x was not modified")
# print()
# try:
#     print("__y", audi.__y)
# except:
#     print("__y is private, so method is needed:")
#     audi.print_y()
# print()
# audi.define()
# print("z was defined:", audi.z)
# try:
#     audi.__print_z()
# except:
#     print("Function print_z is private")
#     audi.printing()