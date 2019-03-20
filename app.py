import json
from cmdb.types import get_instance

jsonstr = """
{
    "type":"cmdb.types.IP",
    "value":"192.168.0.1"
}
"""
obj = json.loads(jsonstr)
a = get_instance(obj['type']).stringify(obj['value'])
print(a)




