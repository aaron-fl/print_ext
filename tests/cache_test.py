from print_ext.cache import cache


class CacheTst():
    
    @cache
    def x(self, a):
        return a


    @cache
    @property
    def y(self):
        self._y += 1
        return self._y

    @y.setter
    def y(self, v):
        self._y = v

    @property
    def z(self):
        print('getz')
    
    @z.setter
    def z(self, v):
        print(f'setz {v}')


class Desc():
    def __init__(self, name):
        self.name = name

    def __get__(self, isntance, owner=None):
        print(f"{self.name} : GET {isntance} {owner}")
        return f"Desc-{self.name}"

    def __set__(self, instance, value):
         print(f"{self.name} : SET {instance} {value}")



class Parent():
    pass

class Jim(Parent):
    
    @cache
    def __len__(self):
        return 0
    


def test_len():
    t = Jim()
    l = len(t)
    t._clear___len__()


def test_cache():
    t = CacheTst()
    t._clear_x()
    t._clear_x()
    assert(t.x(3) == 3)
    assert(t.x(4) == 3)
    t._clear_x()
    assert(t.x(4) == 4)
    assert(t.x(6) == 4)

def test_prop():
    t = CacheTst()
    print(dir(t))
    t._clear_y()
    t.y = 0
    assert(t.y == 1)
    assert(t.y == 1)
    t.y = 9
    assert(t.y == 1)
    t._clear_y()
    assert(t.y == 10)
    assert(t.y == 10)
    

if __name__ == '__main__':
    test_prop()
