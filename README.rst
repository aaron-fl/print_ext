print-ext
=========

Extensions to the print function for printing with a layout engine.



About
=====

The standard python print() function is too simple.  It barely provides any functionality more than just using sys.stdout.write().  This library aims to boost the functionaly/complexity ratio of the print() function.

This is a set of objects for laying out and styling fixed-width text.  The primary use-case is for pretty-printing text to the console to improve console application user interfaces.  But, it can work equally well for any other stream, such as files.

The goal, as always, is to be simple to use the majority of the time while still allowing complex behavior.



Quick Reference
===============

Use
---

>>> from print_ext import print, Printer
>>> print = Printer(width=80) # This is only needed to pass doctests.  Normally just use the print from print_ext.
>>> print('\b1 Hello', ' ', '\b2 World')
Hello World



Pretty Printing
---------------

Lists and dicts can be pretty-printed.

>>> print.pretty({'the':'quick', 'brown':['fox', {'jumped':'over', 'the':'lazy'}, 'dog']})
  the quick
brown [0] fox
      [1] jumped over
             the lazy
      [2] dog


Multi-line Strings
------------------

>>> print(''' This is
...     continued on
...     multiple lines.
...     
...     ''')
This is
continued on
multiple lines.

In order to support this behavor a comprimse had to be made.
Any text with a newline \n in it will be treated as a multi-line string with 
leading and trailing space removed and lines un-indented.

>>> print(' Uh oh\n   this was\n   unexpected!     ')
Uh oh
this was
unexpected!

So replace all your uses of '\n' with '\v' instead.  If you don't have control of the string being displayed then use ``print.print()``, or ``replace('\n','\v')``.

>>> print("  this\v works   ", "better")
  this
 works   better


>>> print.print('This is', 'the same', 'as\n the old', 'print() function', end='!\n')
This is the same as
 the old print() function!




Styles
------

Styles can be applied in two ways: as a keyword parameter, and inline using the escape character \b.  

>>> print('bold ', '\br red-bold ', 'just-bold', style='!')
bold red-bold just-bold

Normally the \b syntax applies only to the string it is defined in.  But adding a $ to the end extends
the influence to the end of the call.

>>> print('white \bb$ blue', ' still blue ', '\b_ blue-underlined', ' just-blue')
white blue still blue blue-underlined just-blue

You can prematurely stop the style with an empty \b or \b$.

>>> print('white \b; dim \b\by$ not-dim-yellow ', 'still-yellow \b$ not-yellow')
white dim not-dim-yellow still-yellow not-yellow

The color codes are: blac(k), (r)ed, (g)reen, (y)ellow, (b)lue, (m)agenta, (c)yan, (w)hite.  bold(!), not-bold(.), dim(;), not-dim(,), underline(_), reset(0)

Background colors are prefixed with a (^). 

>>> print('\bg^c; dim-green-text-on-cyan \b0 back-to-normal ', '\b;! bold-dim \b, bold-not-dim')
dim-green-text-on-cyan back-to-normal bold-dim bold-not-dim

Instead of specifying styles directly, it is recommended to use named styles: err, warn, em, dem, 1, 2, 3.

>>> print('\bem emphasized ', '\bdem de-emphasized ', '\b1 primary-accent ', '\b2 secondary-accent ', '\b3 etc...')
emphasized de-emphasized primary-accent secondary-accent etc...



<hr/>
-----

>>> print.hr()
────────────────────────────────────────────────────────────────────────────────
>>> print.hr('\b1 Hello\nWorld', border_style='2')
                                   │ Hello │
───────────────────────────────────┤ World ├────────────────────────────────────

Vertical and horizontal justification can also be applied.

>>> print.hr('\b1 3...\n2...\n1...\n\br! Blastoff!', just='<^')
─┤ 3...      ├──────────────────────────────────────────────────────────────────
 │ 2...      │
 │ 1...      │
 │ Blastoff! │



Tables
------

>>> from print_ext import Table
>>> tbl = Table(0, 0)
>>> tbl('Hello\tWorld\tこんにちは\t世界\t')
<Table>
>>> print(tbl)
Hello      World
こんにちは 世界

The positional arguments to the Table() call indicate the widths of the colums.  Negative integers specify a fixed-width column.  Positive integers set the minimum width and a ``flex_rate`` of 1.0.  A floating point value specifies the ``flex_rate``

The ``tmpl`` keyword argument specifies a base-set of ``cell()`` calls.  See :ref:`Table.define_tmpl()`

>>> tbl = Table(-6, 4, 10000.0, tmpl='grid')
>>> tbl('1\tThe quick \nbrown fox\tApples\t');
<Table>
>>> tbl('Too long\tjumped over the lazy dog\tBananas\t')
<Table>
>>> print(tbl)
┌─────┬────────────────────────┬───────┐
│1    │The quick               │Apples │
│     │brown fox               │       │
├─────┼────────────────────────┼───────┤
│To…ng│jumped over the lazy dog│Bananas│
└─────┴────────────────────────┴───────┘
>>> tbl.cell('R0', just='>')
>>> print(tbl)
┌─────┬────────────────────────┬───────┐
│    1│              The quick │ Apples│
│     │               brown fox│       │
├─────┼────────────────────────┼───────┤
│To…ng│jumped over the lazy dog│Bananas│
└─────┴────────────────────────┴───────┘
>>> tbl.cell('C0', just='_', style='y')
>>> print(tbl)
┌─────┬────────────────────────┬───────┐
│     │              The quick │ Apples│
│    1│               brown fox│       │
├─────┼────────────────────────┼───────┤
│To…ng│jumped over the lazy dog│Bananas│
└─────┴────────────────────────┴───────┘



Cards
-----

The first cell is the title and the following cells are the body.  So if you don't want a title then tab quickly to the body.

>>> print.card('\tHello\vWorld!')
┌────────┐
│ Hello  │
│ World! │
└────────┘
>>> print.card('\berr Danger', '!\t', "Don't hold plutonium\vwith bare hands.")
┌─────┤ Danger! ├──────┐
│ Don't hold plutonium │
│ with bare hands.     │
└──────────────────────┘



Flex
----

The default print behavior is that of a horizontal wrapping flex.

>>> print('The\vquick brown fox\tJumps over the\v lazy', '\t dog')
The            Jumps over the dog
quick brown fox lazy



Installation
============

.. code-block:: console
   
   $ pip install print-ext


.. image:: https://img.shields.io/pypi/v/print-ext.svg
   :target: https://pypi.org/project/print-ext

   PyPI - Version

.. image:: https://img.shields.io/pypi/pyversions/print-ext.svg
   :target: https://pypi.org/project/print-ext

   PyPI - Python Version



Design decisions
================

Mutable objects:
   It is nice to be able to call a widget multiple times ``tbl(...)`` to add more data.
   This causes some complecations when you try to add some widget to multiple other widgets.

Process-global CVars:
   Context variables can be added to any widget even if it isn't aware of that CVar.
   If you write a custom widget that uses custom CVars then we need to be able to assign that variable on any widget.
   This means that there can't be any namespaces for the CVar names.
   If there is concern of name clashing then use prefix_based_namespacing.

Performance:
   This is designed for human consumption, so it is only fast enough that humans don't get impatient.
   It favors flexability over performance.



Test
====

.. code-block:: console

   $ hatch shell
   $ pytest



License
=======

`print-ext` is distributed under the terms of the `MIT <https://spdx.org/licenses/MIT.html>`_ license.