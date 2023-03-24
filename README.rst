print-ext
=========

A maximally functional, minimally complexity, replacement for the `print()` function and `logging API`.


About
=====

The command line is a powerful user interface.  Just by lining things up and using colors judiciously, you can greatly improve the user experience.

The standard python `print()` function is too simple.  It barely provides any functionally more than just using sys.stdout.write(). 

At the same time, there is the `logging` library that performs a similar function.  It is often not clear whether or not to use `print()` or the `logging` API.

Furthermore, using `print()` with asynchronous tasks is almost meaningless since the output order becomes unclear.

To solve those problems this library introduces the `Printer()`.  It has the following features:

* Adds a ``tag`` keyword parameter that can assign a dictionary of tags to the printed object.  This can be used to filter what gets displayed, eliminating the need to use the `logging` API.  
* Uses `contextvars` to return a special `print()` instance for asynchronous tasks.  This allows the output of those tasks to be captured and displayed in a more user-friendly way.  Having a per-context print() function also allows you to change the tag-filtering on a per-call basis.
* Uses high-level layout widgets to allow simple formatting of complex data with color and wide characters.




Quick Reference
===============

Use
---

>>> print = Printer('\b1 Hello', ' ', '\b2 World')
Hello World
>>> warn = print('Be warned', tag='warn')
Be warned
>>> warn('of bears')
of bears
<print_ext...

The Printer() can print directly, but it also returns a `Printer` in the current context.
Further calls with the returned `Printer` either return itself, or a proxy to itself.
A proxy is returned when a ``tag`` is set.
Then, the proxy `Printer` can be used to print additional messages with the same tag.


Pretty Printing
---------------

Lists and dicts can be pretty-printed.

>>> print.pretty({'the':'quick', 'brown':['fox', {'jumped':'over', 'the':'lazy'}, 'dog']})
  the quick
brown [0] fox
      [1] jumped over
             the lazy
      [2] dog
<print_ext...



Styles
------

Styles can be applied in two ways: as a keyword parameter, and inline using the escape character `\\b`.  

>>> print('bold ', '\br red-bold ', 'just-bold', style='!')
bold red-bold just-bold
<print_ext...

Normally the `\\b` syntax applies only to the string it is defined in.  But adding a $ to the end extends
the influence to the end of the call.

>>> print('white \bb$ blue', ' still blue ', '\b_ blue-underlined', ' just-blue')
white blue still blue blue-underlined just-blue
<print_ext...


You can prematurely stop the style with an empty `\\b` or `\\b$`.

>>> print('white \b; dim \b\by$ not-dim-yellow ', 'still-yellow \b$ not-yellow')
white dim not-dim-yellow still-yellow not-yellow
<print_ext...


The color codes are: blac(k), (r)ed, (g)reen, (y)ellow, (b)lue, (m)agenta, (c)yan, (w)hite.  bold(!), not-bold(.), dim(;), not-dim(,), underline(_), reset(0)

Background colors are prefixed with a (^). 

>>> print('\bg^c; dim-green-text-on-cyan \b0 back-to-normal ', '\b;! bold-dim \b, bold-not-dim')
dim-green-text-on-cyan back-to-normal bold-dim bold-not-dim
<print_ext...


Instead of specifying styles directly, it is recommended to use named styles: err, warn, em, dem, 1, 2, 3.

>>> print('\bem emphasized ', '\bdem de-emphasized ', '\b1 primary-accent ', '\b2 secondary-accent ', '\b3 etc.')
emphasized de-emphasized primary-accent secondary-accent etc.
<print_ext...


<hr/>
-----

>>> print.hr()
────...
<print_ext...
>>> print.hr('\b1 Hello\nWorld', border_style='2')
 │ Hello │
─┤ World ├─────...
<print_ext...

Vertical and horizontal justification can also be applied.

>>> print.hr('\b1 3...\n2...\n1...\n\br! Blastoff!', just='<^')
─┤ 3...      ├───────...
 │ 2...      │
 │ 1...      │
 │ Blastoff! │
<print_ext...

The lines drawn are taken from the ``border`` context variable.

>>> print.hr('BOLD', border=('#','-.rl'))
━┥ BOLD ┝━━━...
<print_ext...
>>> print.hr("This\nall looks right\njustified", border=' ', just='>')
                                                                         This
                                                              all looks right
                                                                    justified
<print_ext...



Tables
------

>>> from print_ext import Table
>>> tbl = Table(0, 0)
>>> tbl('Hello\tWorld\tこんにちは\t世界\t')
<print_ext.table.Table...
>>> print(tbl)
Hello      World
こんにちは 世界
<print_ext...

The positional arguments to the Table() call indicate the widths of the columns.  Negative integers specify a fixed-width column.  Positive integers set the minimum width and a ``flex_rate`` of 1.0.  A floating point value specifies the ``flex_rate``

The ``tmpl`` keyword argument specifies a base-set of ``cell()`` calls.  See `Table.define_tmpl()`

>>> tbl = Table(-6, 4, 10000.0, tmpl='grid')
>>> tbl('1\tThe quick \nbrown fox\tApples\t');
<print_ext.table.Table...
>>> tbl('Too long\tjumped over the lazy dog\tBananas\t')
<print_ext.table.Table...
>>> print(tbl)
┌─────┬────────────────────────┬───────┐
│1    │The quick               │Apples │
│     │brown fox               │       │
├─────┼────────────────────────┼───────┤
│Too l│jumped over the lazy dog│Bananas│
│⤷ ong│                        │       │
└─────┴────────────────────────┴───────┘
<print_ext...
>>> tbl.cell('R0', just='>')
>>> print(tbl)
┌─────┬────────────────────────┬───────┐
│    1│              The quick │ Apples│
│     │               brown fox│       │
├─────┼────────────────────────┼───────┤
│Too l│jumped over the lazy dog│Bananas│
│⤷ ong│                        │       │
└─────┴────────────────────────┴───────┘
<print_ext...
>>> tbl.cell('C0', just='_', style='y', wrap=False)
>>> print(tbl)
┌─────┬────────────────────────┬───────┐
│     │              The quick │ Apples│
│    1│               brown fox│       │
├─────┼────────────────────────┼───────┤
│To⋯ng│jumped over the lazy dog│Bananas│
└─────┴────────────────────────┴───────┘
<print_ext...


Progress
--------

>>> files = [f'{chr(i+65)*((i%10)+3)}.py' for i in range(26)]
>>> with print.progress(f'Processing \bem {len(files)}\b  files') as update:
...     for i, fname in enumerate(files):
...         update(f'Process #{i} {fname}', tag={'progress':(i, len(files))})
...     update("Done Processing files", tag='progress:100')
<print_ext...
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ Processing 26 files Done Processing files
<print_ext...
>>> print("Continue more work")
Continue more work
<print_ext...




Cards
-----

The first cell is the title and the following cells are the body.  So if you don't want a title then tab quickly to the body.

>>> print.card('\tHello\nWorld!')
┌────────┐
│ Hello  │
│ World! │
└────────┘
<print_ext...
>>> print.card('\berr Danger', '!\t', "Don't hold plutonium\nwith bare hands.")
┌┤ Danger! ├───────────┐
│ Don't hold plutonium │
│ with bare hands.     │
└──────────────────────┘
<print_ext...


Flex
----

A flex, like a Table, uses tab characters to move from cell to cell.

>>> print.flex('The\nquick brown fox\tJumps over the\n lazy', '\t dog')
The            Jumps over the dog
quick brown fox lazy
<print_ext...
>>> from print_ext import Bdr
>>> bdr = Bdr(border=('m:0001','-.r'), flex_rate=0)
>>> print.flex(bdr('\berr Error: '), '\t', 'The quick brown\nfox jumped over\nthe lazy\ndog.')
Error: │The quick brown
       │fox jumped over
       │the lazy
       │dog.
<print_ext...


Installation
============

.. code-block:: console
   
   $ pip install print-ext


.. image:: https://img.shields.io/pypi/v/print-ext.svg
   :target: https://pypi.org/project/print-ext


.. image:: https://img.shields.io/pypi/pyversions/print-ext.svg
   :target: https://pypi.org/project/print-ext



Design decisions
================

Mutable objects:
   It is nice to be able to call a widget multiple times ``tbl(...)`` to add more data.
   This causes some complications when you try to add some widget to multiple other widgets.

Process-global CVars:
   Context variables can be added to any widget even if it isn't aware of that CVar.
   If you write a custom widget that uses custom CVars then we need to be able to assign that variable on any widget.
   This means that there can't be any namespaces for the CVar names.
   If there is concern of name clashing then use prefix_based_namespacing.

Performance:
   This is designed for human consumption, so it is only fast enough that humans don't get impatient.
   It favors flexibility over performance.



Test
====

.. code-block:: console

   $ hatch shell
   $ pytest



License
=======

`print-ext` is distributed under the terms of the `MIT <https://spdx.org/licenses/MIT.html>`_ license.
