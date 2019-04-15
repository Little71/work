import importlib
import ipaddress  # 3.3版本才有

# 类和实例的缓存字典
clsaaes_cache = {}
instance_cache = {}


def get_class(type: str):
    cls = clsaaes_cache.get(type)
    if cls:
        return cls

    # m, c = type.rsplit('.', maxsplit=1)
    # # '''插件化实现，需要的时候就动态加载，不会重复加载'''
    # # mod = importlib.import_module(m)
    # cls = getattr(mod, c)
    #
    # globals().get(type)
    #
    # clsaaes_cache[type] = cls
    #
    # if issubclass(cls, BaseType):
    #     return cls
    # raise TypeError(f'Wrong Type! {cls} is not sub class of {BaseType}.')


#"cmdb.types.Int"  "Int" 两种名称
def get_instance(type: str, **option):
    '''
    :param type: 参数类型
    :param option: 参数规则
    :return:
    '''
    option_key = ",".join(f"{k}={v}"for k, v in sorted(option.items()))
    key = f"{type}:{option_key}"
    # 如验证规则option改变，所以不同的规则，实例行为不同，所以要把规则加进去
    '''
    解决频繁创建实例的事情，创建越少，垃圾回收就越少，否则要清理大量的垃圾，垃圾清理的性能就越差
    要清理调整，是因为有很多内存碎片都是不想要的，拿走就变成了内存空洞，这就要处理规整了
    规整之后，就会有连续的大内存了，不然这些连续的内存都是千疮百孔
    '''
    instance = instance_cache.get(key)
    if instance:
        return instance

    instance = get_class(type)(**option)
    instance_cache[key] = instance
    return instance

'''
因为在导入模块的函数的时候，模块已经加载了，所以可以直接通过globals()获取当前模块的名词空间的属性字典
然后通过一些条件，把用户所需的类获取到，无论是长名称还是短名称
'''
def inject():
    for n,t in globals().items():
        if type(t)== type and issubclass(t,BaseType) and n != 'BaseType':
            clsaaes_cache[n] = t
            clsaaes_cache[f"{__name__}.{n}"] = t

class BaseType:
    def __init__(self, **option):
        '''option -> dict'''
        self.__dict__['option'] = option

    def __getattr__(self, item):
        return self.option.get(item)

    def __setattr__(self, key, value):
        raise NotImplementedError()

    def stringify(self, value):
        raise NotImplementedError()

    def destringify(self, value):
        raise NotImplementedError()


class Int(BaseType):

    def stringify(self, value):
        val = int(value)
        # max = self.option.get('max')
        # max = self.get('max')
        max = self.max
        if max and val > max:
            raise ValueError(f'{val} Too Big')
        min = self.option.get('min')
        if min and val < min:
            raise ValueError(f'{val} Too Small')

        # 要将int序列化，即要先是int类型,因为是存储的数据类型是text，所以只能是str
        return str(val)

    def destringify(self, value):
        return int(value)


class IP(BaseType):
    def stringify(self, value):
        '''传入ip字符串或者数字,转换错误不要给默认值，在外面处理'''
        val = str(ipaddress.ip_address(value))
        if not val.startswith(self.prefix):
            raise ValueError(f'{val} not startswith to {self.prefix}')
        return val

    def destringify(self, value):
        return value

#加载类到字典
inject()

print(clsaaes_cache )
print(instance_cache)