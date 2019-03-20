import importlib
import ipaddress  # 3.3版本才有


def get_instance(type: str):
    '''插件化实现，需要的时候就动态加载'''
    m, c = type.rsplit('.', maxsplit=1)
    mod = importlib.import_module(m)
    cls = getattr(mod, c)
    obj = cls()
    if isinstance(obj, BaseType):
        return obj
    raise TypeError(f'Wrong Type! {obj} is not sub class of {BaseType}.')


class BaseType:

    def stringify(self, value):
        raise NotImplementedError()

    def destringify(self, value):
        raise NotImplementedError()


class Int(BaseType):

    def stringify(self, value):
        # 要将int序列化，即要先是int类型,因为是存储的数据类型是text，所以只能是str
        return str(int(value))

    def destringify(self, value):
        return int(value)


class IP(BaseType):
    def stringify(self, value):
        '''传入ip字符串或者数字,转换错误不要给默认值，在外面处理'''
        return str(ipaddress.ip_address(value))

    def destringify(self, value):
        return value
