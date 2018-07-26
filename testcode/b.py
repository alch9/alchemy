


def greet(name):
    return "hello " + name


#This is a global comment

#1. This is a test doc
#2. This is a test doc
def add(a, b, dryrun=False):
    """
    a: Integer a
    b: Integer b
    out:
        result: Addition of a + b
    """

    if dryrun:
        return {'result': None}

    return {
        'result': a+b
    }

# Multiply numbers
def mul(a, b, dryrun=False):
    """
    a: Integer a
    b: Integer b
    out:
        result: Multiplication of a + b
    """
    if dryrun:
        return {'result': 'add'}
    return { 'result': a * b}

def test(a,b, c = None, d = 1):
    print a, b, c, d

def test2():
    pass

def test3(a=1, b=2):
    pass
