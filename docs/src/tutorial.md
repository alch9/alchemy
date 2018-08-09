
# Tutorial

Pre-requisites:

1. Alchemy is installed and is in PYTHONPATH
2. Have read the core concepts


Here is the objective of the tutorial:

1. Create a math module, which consists of basic functions like addition & multiplication
2. Using these basic functions (also called units), compute \\( (a+b)^2 \\) for a given `a` & `b`

While doing the above, you will learn about the follwing core concepts:

1. Unit
2. Flow - Chaining units
3. Config files
4. Chaining the flows


### Math module

Create a python module:

```bash
mkdir mymath
touch mymath/__init__.py
```

Define functions for addition & multiplication in `mymath/__init__.py`

```python

def add(a, b):
   return {'add_val': a+b}

def mul(a, b):
   return {'mul_val': a*b}
```

Now, returning a dict might seem to be an overkill right now, but this will be elaborated later.

As stated earlier, we will "chain" these functions in such a way that it will compute \\( (a+b)^2 \\) for a given `a` & `b`.


### Alchemy config

First we need to 'register' these functions in config file. Config file has the same name that of the module and it needs to be in the module dir as mentioned below:

```bash
touch mymath/mymath.yml
```

Config file is a Yaml file which needs to have the following entries, which identifies it as a Yaml file meant for Alchemy framework.
If this basic header info is not present, then the framework will not identify it as a valid config file and will simply ignore it.

```yaml
alchemy:
   cfg_version: 1.0
```

Let's register the units:

```yaml
alchemy:
   cfg_version: 1.0

include: [alchemy]

units:
    add-num:
        desc: Adds two integers
        func: mymath.add
        input:
            a: Integer 1
            b: Integer 2
        output:
            add_val: Result of the addition
    mul-num:
        desc: Multiplies two integers
        func: mymath.mul
        input:
            a: Integer 1
            b: Integer 2
        output:
            mul_val: Result of the multiplication
```

The config defines two units, `add-num` and `mul-num`. The names can be different from the actual function name. We describe the units in terms of attributes which are explained below:

* `desc`: Description of the unit
* `func`: Importable python function described in python's dot syntax.
* `input`: Yaml dict where each key is the input argument and value the description of the argument. The argument name should match the function name
* `output`: Description of values items/entities which the function returns. In the `add`, we return `add_val`, so we describe it

The `include: [alchemy]` means that we want to use all units & flows defined in `alchemy` module

**Note**:
* The framework checks arguments in `input` against the actual names defined in the function. So if the names of the function arguments are changed, then the config also needs to be updated. Failing to do so will result into an error.
* The order of `a` & `b` defined under `input` does not matter. `b` could have been very well defined first.



### List units

Let's see if the units & the config are parsed by the framework or now.


```bash
<path to alchemy dir>/alchemy/alch.py listu mymath
```

The command `listu` lists the units defined in `mymath` module and you should see something like:

```
...
------------------------------------------
16  add-num
------------------------------------------
17  mul-num
------------------------------------------
...
```

Note: 
* This assumes that you have `alchemy` & `mymath` folders are in `PYTHONPATH`.
* The numbers `16` & `17` are sequence numbers for the units and these could vary for you as more units are added in `alchemy`



### Flow

We now "chain" the `add-num` & `mul-num` units to create compute \\( (a+b)^2 \\). To do this, we create a flow called `binomial`:


```yaml
alchemy:
   cfg_version: 1.0

units:
    add-num:
        desc: Adds two integers
        func: mymath.add
        input:
            a: Integer 1
            b: Integer 2
        output:
            add_val: Result of the addition
    mul-num:
        desc: Multiplies two integers
        func: mymath.mul
        input:
            a: Integer 1
            b: Integer 2
        output:
            mul_val: Result of the multiplication

flows:
    binomial:
        desc: Computes binomial expression
        input:
        output:
        units:
            - add-num:
                a: 2
                b: 3
            - mul-num:
                a: $add_val
                b: $add_val
            - print-context:
                param_list: [mul_val]
    
```

We define all flows under `flows` and the flow `binomial` is defined in terms of the attributes:
* `desc`: Description of the flow
* `input`: Yaml dict (which is empty here) where key is the argument name and value is its description.
* `output`: Yaml dict (which is empty here) where key is the param which is returned by the flow and values is is description
* `units`: List of units to be run in the sequence (note the hypens `-`)


Let's understand how this works:

Have a look at `add-num`

```yaml
- add-num:
    a: 2
    b: 3
```

The unit `add-num` is called with params `2` & `3`. This is equivalent to the funciton call: `mymath.add(2,3)`. The order of `a` and `b` does not matter here.

The return value of this function is a dict and add its key-value's are stored in framework's context. So at the end of the `add` call, the framework has `add_val` in the context with value `5`

Now look at mul-num

```yaml
- mul-num:
    a: $add_val
    b: $add_val
```

This calls the function `mymath.mul`. But, the `$` tells the framework that we want to pass the value in `add_val` as argument `a` and `b`. The `mul` also returns a dict with key `mul_val`. So at the end of the `mul` call, context has `mul_val` with value `25`. It also has `add_val` still in the context.

This brings us to the `print-context`. 

```yaml
- print-context:
    param_list: [mul_val]
```

Where is it defined? Remember the `include: [alchemy]`? It is defined in `alchemy` module. It takes the list of param names as input and prints their values on STDOUT. So here we want to see the value of `mul_val`. 


### Running the flow

First, check if alchemy knows about our flow:

```bash
<path to alchemy dir>/alchemy/alch.py listf mymath
```

This should list the flows:

```bash
1  create-module
2  create-module-cli
3  thread-test
4  binomial
```

The actual list you may get could be different. The important thing is that you should see the flow `binomial` in the list

Let's run the flow:

```bash
<path to alchemy dir>/alchemy/alch.py run mymath binomial
```

This should give output like:

```bash
>> add-num
>> mul-num
>> print-context
--- ctx start --
mul_val = 25
--- ctx end --
```

To recap, we chained the simple `add` & `mul` to create a something complex in a simple declarative manner.


### Flow chaining

You can also chain other flows from a flow. So we will create a flow called `square` and use it in `binomial`:

```yaml
flows:
    square:
        desc: Computes a square of the an integer
        input:
            n: An integer
        output:
            sq_result: Square value of n
        units:
            - mul-num:
                a: $n
                b: $n
            - context:
                varmap:
                    sq_result: $mul_val
```

The flow `square` takes integer described in input as `n: ...` and it promises to return the output in `sq_result` defined in `output`.

The `context` is defined in `alchemy`. It defines new things in framework context like here it is defining `sq_result` as same value as that of `mul_val` (indicated by `$`). The `mul_val` is made available by `mul-num`.

Let's use `square` in `binomial`:

```yaml
flows:
    square:
        desc: Computes a square of the an integer
        input:
            n: An integer
        output:
            sq_result: Square value of n
        units:
            - mul-num:
                a: $n
                b: $n
            - context:
                varmap:
                    sq_result: $mul_val
    binomial:
        desc: Computes binomial expression
        input:
        output:
        units:
            - add-num:
                a: 2
                b: 3
            - $square:
                n: $add_val
            - print-context:
                param_list: [sq_result]
```

Here we are "chaining" the flow `square` by pre-fixing `$`. The input argument name `n` should match the name defined in the `input` of the flow. Since the return value of the flow is `sq_result` we print it in `print-context`. 

Note: The intermediate context values generated in the flow are not available in the flow which it is called. So, the `mul_val` which the `mul-num` exports in `square` is not available in `binomial`.


### Parameterize the flow

The binomial flow only computes fixed values as arguments. To make it generic, there are several units already defined which can be chained with binomial. We could define the two integers in a yaml file like below and then read it as input:

```yaml
binomial-params:
    x: 3
    y: 4
```

So what we need is to our flow to read x & y from the above yaml and plug that into the remaining units. We use units `load-yaml-file` & `query-dict` to achieve this.

(Only the relevant part of the yaml is shown for brevity)
```yaml
...
    binomial:
        desc: Computes binomial expression
        input:
        output:
        units:
            - load-yaml-file:
                filepath: params.yml
            - query-dict:
                dict_var: $yaml_data
                pathmap:
                    p: binomial-params/x
                    q: binomial-params/y
            - add-num:
                a: $p
                b: $q
            - $square:
                n: $add_val
            - print-context:
                param_list: [sq_result]
```

The `load-yaml-file` parses `params.yml` and returns its content as python dict `yaml_data` which is fed as input to `query-dict`. The `query-dict` as the names suggests, queries a python dict `dict_var` using paths defined in `pathmap`. Each key in `pathmap` is exported with value defined against the nested path defined as value.

Do not worry if you do not understand fully what these units do. The only take-away here is that we parsed a yaml file containing params and chained them to the rest of the flow.

One issue remains though. The input params file name is now hardcoded. We could take the params file name as CLI using `cli-positional` unit:

```yaml
...
    binomial:
        ...
        units:
            - cli-positional:
                spec: [params_file]
            - load-yaml-file:
                filepath: $input_params_file
        ...
```

The only change we made here is that we used `cli-positional` which parses `sys.argv` as simple positional arguments against the `spec`. For each `x` in `spec` it exports `input_x` and hence we use `input_params_file` as input in `load-yaml-file`.
