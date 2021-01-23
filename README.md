[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

# Pascal Compiler
Lightweight modular Pascal compiler with an interpreter and C code generator.

<img src="https://i.postimg.cc/SNmFQ6X0/pp-01.png"/>

## Structure
* **Lexer** - Converting a sequence of characters into a sequence of token-value pairs
* **Parser** - Building the AST while conforming to the rules of a formal grammar
* **Symbolizer** - Visits the AST and forms symbols table
* **Generator** - Produces C code using the symbols and AST
* **Runner** - Interpreting AST

## Usage

1. Choose the test file from [01-11] in ```main.py```

2. Compile and run example Pascal code
```bash
python3 main.py
```

3. Runner will be executed. Enter the input values from the specified test folder or any other you'd like to try.

4. Generated code with be placed inside the specified test folder.
