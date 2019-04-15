import json
from pprint import pprint

from cmdb.types import get_instance

jsonstr = """
{
    "type":{
        "name":"cmdb.types.IP",
        "option":{
            "perfix":"192.168"
            }
    },
    "value":"192.168.0.1,192.168.0.2",
    "nullable":true,
    "unique":false,
    "default":"",
    "multi":true,
    "reference":{
        "schema":"ippool",
        "field":"ip",
        "on_delete":"cascade|set_null|disbale",
        "on_update":"cascade|disbale"
    }
}
"""
#简写的type
jsonstr1 = """
{
    "type":"cmdb.types.IP",
    "unique":true
}
"""

# obj = json.loads(jsonstr)
# a = get_instance(obj['type'],**obj.get('option',{}))
#
# a = a.stringify(obj['value'])
#
# print(a)


def a():
    return None is not None
print(a())
