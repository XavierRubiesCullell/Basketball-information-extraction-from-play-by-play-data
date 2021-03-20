import Prova

class Cotxe():
    def __init__(self):
        self.mercedes = Prova.Car()
        self.ostra = 0
        self.modify()
        hola = "pim"

    def modify(self):
        self.ostra = 1

    def print_hola(self):
        print(hola)

    def define_adeu(self):
        vars(self)["adeu"] = "adeeeeeeeu"

    def print_vars(self):
        print(vars(self))

a = Cotxe()
print(a.mercedes.x)
print("ostra:", a.ostra)
try:
    a.print_hola()
except:
    print("hola no és accessible")

print("variables")
print(vars(a))

print(1 in vars(a))

print(vars(a)["o"+"stra"])


a.print_vars()
a.define_adeu()
a.print_vars()