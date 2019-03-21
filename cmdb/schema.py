import logging
import math

from cmdb.models import session,Schema,Field,Entity,Value
logger = logging.getLogger(__name__)

#schema接口
# 返回一个schema对象
def get_schema_by_name(name:str,delete:bool=False):
    query = session.query(Schema).filter(Schema.name == name.strip())
    if not delete:
        query = query.filter(Schema.delete==False)
    return query.first()

#增加一个schema
def add_schema(name:str,desc:str=None):
    schema = Schema()
    schema.name = name.strip()
    schema.desc = desc
    session.add(schema)
    try:
        session.commit()
        return schema
    except Exception as e:
        session.rollback()
        logger.error(f'Fail to add a new schema {schema} . Error:{e}')









