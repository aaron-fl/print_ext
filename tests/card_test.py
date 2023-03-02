from print_ext.card import Card
from .testutil import flat, printer
from print_ext.flex import Flex


def test_card_hello():
    c = Card('hello\t', 'to the great big\vworld')
    assert(flat(c) == [
        '┌────┤ hello ├─────┐',
        '│ to the great big │',
        '│ world            │',
        '└──────────────────┘',])


def test_card_multi_title():
    assert(flat(Card('a\vb\vc\tinner body\t')) == [
        '    │ a │     ',
        '    │ b │     ',
        '┌───┤ c ├────┐',
        '│ inner body │',
        '└────────────┘',   
    ])


def test_card_empty():
    assert(flat(Card()) == ['┌──┐', '└──┘'])


def test_card_notitle():
    assert(flat(Card('\tHello to the\vworld')) == [
        '┌──────────────┐', 
        '│ Hello to the │', 
        '│ world        │', 
        '└──────────────┘'])



def test_card_clone():
    c = Card('title\tbody')
    f = Flex(c, '\t', c)
    assert(flat(f) == ['┌┤ title ├┐┌┤ title ├┐', '│ body    ││ body    │', '└─────────┘└─────────┘'])
