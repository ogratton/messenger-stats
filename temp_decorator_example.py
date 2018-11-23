# because I couldn't remember how to set function flags with decorators before

def dec(f):
    def _f(*a, **b):
        return f(*a, **b)
    _f.flag = True
    return _f

@dec
def g(name):
    print("Hi, %s!" % name)
    
print(g.flag)

print(g("Barbara"))
