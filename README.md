# print-ext

This is a set of objects for laying out and styling fixed-width text.  The primary use-case is for pretty-printing text to the console to improve console application user interfaces.  But, it can work equally well for any other stream, such as files.

The goal is to be simple to use the majority of the time while still allowing complex behavior.

# Quick Reference

## Use

>>> from print_ext import print

## Styles

## Tables

## <hr/>

## Progress Bar

-----

# Installation

```console
$ pip install print-ext
```

[![PyPI - Version](https://img.shields.io/pypi/v/print-ext.svg)](https://pypi.org/project/print-ext)
[![PyPI - Python Version](https://img.shields.io/pypi/pyversions/print-ext.svg)](https://pypi.org/project/print-ext)


# Design decisions

Mutable objects:  I want to be able to append to an object with ``obj(...)``.

Process-global CVars:  I want to be able to define a context variable on any object and their meaning must stay consistant.

# Test

```console
$ hatch shell
$ pytest
```


# License

`print-ext` is distributed under the terms of the [MIT](https://spdx.org/licenses/MIT.html) license.
