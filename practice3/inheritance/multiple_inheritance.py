class Father:
    def work(self):
        print("Father works")

class Mother:
    def care(self):
        print("Mother cares")

class Child(Father, Mother):
    pass

c = Child()
c.work()
c.care()
