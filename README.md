# Alchemy - Automation framework


## What is it?

A new minimalistic backend automation framework for Python 2.7. The approach is to write simple python functions and assemble them to create a meaningfull flow.


## How does it look like?

Suppose you have a functions to add 2 numbers and multiply 2 numbers in `mymath` module
```python
def add(a, b):
    return {'result': a+b}

def mul(a, b):
    return {'result': a*b}
```

You can use it like in a yaml config file:

```yaml
alchemy:
    cfg_version: 1.0

units:
    add-num:
        desc: Add 2 numbers
        func: mymath.add
        input:
            a: Integer 1 
            b: Integer 2 
        output:
            result: Computation result of addition
    mul-num:
        desc: Multiply 2 numbers
        func: mymath.mul
        input:
            a: Integer 1 
            b: Integer 2 
        output:
            result: Computation result of multiplication
```

* The `add` & `mul` function are simple functions which are called a `unit`s and we have registered it as `add-num` & `mul-num` respectively in yaml config file
* Each python module which has such units needs to have a config yaml file with the same name. So if your python module name is `X` then the framework looks for config file as `X.yml` at the folder `X/X.yml'

Now we use this unit to add numbers:


```yaml
alchemy:
    cfg_version: 1.0

units:
    add-num:
        desc: Add 2 numbers
        func: mymath.add
        input:
            a: Integer 1 
            b: Integer 2 
        output:
            result: Computation result of addition

flows:
    add-test:
        desc: Testing addition
        input:
        output:
        units:
            - add-num:
                a: 10
                b: 20
```

* We added a flow called `add-test`. Flow is simply a sequence of units
* When we run this flow nothing will get printed on the screen. For that we need to include another config

```yaml
alchemy:
    cfg_version: 1.0

include: [alchemy]
...
```

* We can inherit from other configs. In this case we want to use all the units and flows in `alchemy` module.
* Let's print the result


```yaml
...
flows:
    add-test:
        desc: Testing addition
        input:
        output:
        units:
            - add-num:
                a: 10
                b: 20
            - print-context:
                param_list: [result]
```
