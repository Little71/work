# field接口
# 获取字段
from cmdb.models import session, Field, Entity, FieldMeta, Value
from cmdb.schema import get_schema_by_name, logger


def get_field(schema_name, field_name, delete=False):
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError(f"{schema_name} is not Tablename")

    query = session.query(Field).filter(Field.name == field_name)
    if not delete:
        query = query.filter(Field.delete == False)
    return query.first()


# 逻辑表是否已经使用
def table_used(schema_id, delete=False):
    query = session.query(Entity).filter(Entity.schema_id == schema_id)
    if not delete:
        query = query.filter(Entity.delete == False)
    return query.first() is not None


def _add_field(field):
    session.add(field)
    try:
        session.commit()
        return field
    except Exception as e:
        session.rollback()
        logger.error(f'commit faild. Error:{e}')
        raise e


# 两种情况，1完全新增，2已有表增加字段
def add_field(schema_name, name, meta):
    schema = get_schema_by_name(schema_name)
    if not schema:
        raise ValueError(f"{schema_name} is not Tablename")

    # 解析meta
    meta_data = FieldMeta(meta)
    field = Field()
    field.name = name.strip()
    field.schema_id = schema.id
    field.meta = meta  # 解析成功说明符合格式要求

    # ref_id引用
    if meta_data.reference:
        ref_schema = meta_data.reference.schema
        ref_field = meta_data.reference.field
        ref = get_field(ref_schema, ref_field)
        if not ref:
            raise TypeError(f"Wrong Reference {ref_schema}.{ref_field}")
        field.ref_id = ref.id

    # 判断字段是否已经使用
    if not table_used(schema.id):
        # 如未使用逻辑表，直接增加字段
        return _add_field(field)

    # 已使用逻辑表
    if meta_data.nullable:
        # 可以为空则直接添加
        return _add_field(field)

    # 到这里已有一个隐含条件即不可为空
    if meta_data.unique:  # 如必须唯一
        # 当前条件对一个正在使用的逻辑表加字段不可为空又要唯一，做不到
        raise TypeError("This field is not required an unique")

    # 到这里隐含条件是，不可为空，但不唯一
    if not meta_data.default:
        # 没有缺省值
        raise TypeError('This field requires a default value')
    else:
        # 为逻辑表所有记录增加字段，操作entity表
        for entity in iter_entities(schema.id):
            value = Value()
            value.entity_id = entity.id
            value.field = field #这时候还没生成field.id，只能通过sqlalchemy的外键约束去填充
            value.value = meta_data.default
            session.add(value)
        return _add_field(field)


def iter_entities(schema_id, patch=100):
    page = 1
    while True:
        query = session.query(Entity).filter((Entity.schema_id == schema_id) & (Entity.delete == False))
        reuslt = query.limit(patch).offset(patch * (page - 1))
        if not reuslt:
            return None
        yield from reuslt
        page += 1
