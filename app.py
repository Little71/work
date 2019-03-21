import json
from cmdb.types import get_instance

jsonstr = """
{
    "type":"cmdb.types.Int",
    "value":80,
    "nullable":true,
    "unique":false,
    "option":{
        "max":100,
        "min":1
    },
    "multi":true
    "reference":{
        "schema":1,
        "field":1,
        "on_delete":cascade|set_null|disbale,
        "on_update":cascade|disbale,
    }
}
"""
obj = json.loads(jsonstr)
a = get_instance(obj['type'],**obj.get('option',{})).stringify(obj['value'])
print(a)


