import pytest
from print_ext.card import Card
from print_ext.line import SMark as SM
from print_ext.flex import Flex
from .testutil import flat, styled


def test_card_hello():
    c = Card('hello\t', 'to the great big\vworld')
    assert(flat(c) == [
        '┌┤ hello ├─────────┐',
        '│ to the great big │',
        '│ world            │',
        '└──────────────────┘',])


def test_card_multi_title():
    assert(flat(Card('a\vb\vc\tinner body')) == [
        ' │ a │        ',
        ' │ b │        ',
        '┌┤ c ├───────┐',
        '│ inner body │',
        '└────────────┘',   
    ])


def test_card_empty():
    assert(flat(Card()) == ['┌──┐', '│  │', '└──┘'])


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



def test_border_hilite_bug():
    ''' Show a portion of the table while building.  The col widths may change, so use fixed col widths
    '''
    c = Card('\berr Error:\t', 'Some problem')    
    assert(styled(c) == [
        ('┌┤ Error: ├────┐', [SM('dem',0,3), SM('err',3,9), SM('dem',9,16)]),
        ('│ Some problem │', [SM('dem',0,2), SM('dem',14,16)]),
        ('└──────────────┘', [SM('dem',0,16)]),
    ])


@pytest.mark.xfail(reason="implement")
def test_card_obey_max_width():
    assert(False)

    