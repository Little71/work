import logging
import math

from cmdb.models import session, Schema, Field, Entity, Value

logger = logging.getLogger(__name__)


# schema接口
# 返回一个schema对象
def get_schema_by_name(name: str, delete: bool = False):
    query = session.query(Schema).filter(Schema.name == name.strip())
    if not delete:
        query = query.filter(Schema.delete == False)
    return query.first()


# 增加一个schema
def add_schema(name: str, desc: str = None):
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
        raise


# 删除使用id，id唯一，比使用name删除好
def delete_schema(id: int):
    try:
        schema = session.query(Schema).filter((Schema.id == id) & (Schema.delete == False))
        if schema:
            # 如删除多个同名标，可用数字递增进行表示删除的是哪个避免冲突
            schema.delete = True
            session.add(schema)
            try:
                session.commit()
                return schema
            except Exception as e:
                session.rollback()
                raise e
        else:
            raise ValueError(f'Wrong ID {id}')
    except Exception as e:
        logger.error(f'Fail to del a schema. id = {id}. Error:{e}.')


# 列出所有逻辑表
def list_schema(page: list, size: int, deleted: bool = False):
    query = session.query(Schema)
    if not deleted:
        query = query.filter(Schema.delete == False)
    return list(paginate(page, size, query))


def paginate(page, size, query):
    try:
        page = page if page > 0 else 1
        size = size if 0 < size < 100 else 20
        count = query.count()
        pages = math.ceil(count / size)
        while True:
            result = query.limit(size).offset(size * (page - 1))
            if not result:
                return None
            yield from result, (page, size, count, pages)
            page +=1
    except Exception as e:
        logger.error(f'Error:{e}.')
