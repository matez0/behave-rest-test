[![Python versions](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/)
[![license](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

# behave-rest-test

This is an example how to perform
[behavior-driven development](https://en.wikipedia.org/wiki/Behavior-driven_development) (BDD)
based on [behave](https://github.com/behave/behave)
to specify and test a REST API.

The presented micro-framework provides [gherkin](https://cucumber.io/docs/gherkin/reference/)
patterns for a higher level description unlike other available frameworks.

## Self test

Create the virtual environment:
```
python -m venv .venv
. .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

Run the tests:
```
BEHAVE_RESTEST_SELF_TEST=on behave
```
