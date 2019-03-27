import json
import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, BigInteger, Boolean, Text
from sqlalchemy import Column, ForeignKey, create_engine, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker, relationship

from .types import get_instance


Base = declarative_base()
conn = "mysql+pymysql://game:aohe123456@192.168.0.202:3306/test_person"
engine = create_engine(conn, encoding="utf-8", echo=True)

Session = sessionmaker()
session = Session(bind=engine)


class Schema(Base):
    __tablename__ = 'schema'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=False, unique=True)
    desc = Column(String(128), nullable=False)
    delete = Column(Boolean, nullable=False, default=False)

class Reference:
    def __init__(self,ref:dict):
        self.schema = ref['schema'] #引用的schema
        self.field = ref['field'] #引用的field
        self.on_delete = ref.get('on_delete','disable') #cascade,set_null,disbale
        self.on_update = ref.get('on_update','disable') #cascade,disbale

class FieldMeta:
    def __init__(self,metastr:str):
        meta = json.loads(metastr)

        if isinstance(meta['type'],str):
            self.instance = get_instance(meta['type'])
        else:
            option = meta['type'].get('option')
            if option:
                self.instance = get_instance(meta['type']['name'],**option)
            else:
                self.instance = get_instance(meta['type']['name'])
        self.unique = meta.get('unique',False)
        self.nullable = meta.get('nullable',True)
        self.default = meta.get('default')
        self.multi = meta.get('multi',False)
        #引用是一个json对象
        ref = meta.get('reference')
        if ref:
            self.reference = Reference(ref)
        else:
            self.reference = None


class Field(Base):
    __tablename__ = 'field'
    __table_args__ = (UniqueConstraint('schema_id', 'name', ),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=False)
    schema_id = Column(Integer, ForeignKey('schema.id'), nullable=False)
    meta = Column(Text, nullable=False)
    ref_id = Column(Integer, ForeignKey('field.id'), nullable=False)
    delete = Column(Boolean, nullable=False, default=False)

    schema = relationship('Schema')
    field = relationship('Field', uselist=False)  # 1对1，被应用的id

    #增加一个属性将meta解析成对象，主要不要使用metadata这个名字
    @property
    def meta_data(self):
        return FieldMeta(self.meta)


class Entity(Base):
    __tablename__ = 'entity'
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(64), nullable=False)
    schema_id = Column(Integer, ForeignKey('schema.id'), nullable=False)
    delete = Column(Boolean, nullable=False, default=False)

    schema = relationship('Schema')


class Value(Base):
    __tablename__ = 'value'
    __table_args__ = (UniqueConstraint('entity_id', 'field_id', name='uq_entity_field'),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    value = Column(Text, nullable=False)
    field_id = Column(Integer, ForeignKey('field.id'), nullable=False)
    entity_id = Column(BigInteger, ForeignKey('schema.id'), nullable=False)
    delete = Column(Boolean, nullable=False, default=False)

    entity = relationship('Entity')
    field = relationship('Field')


def createalltables(tables=None):
    Base.metadata.create_all(engine, tables)


def dropalltables():
    Base.metadata.drop_all(engine)


def showstace(instance):
    from sqlalchemy import inspect
    ins = inspect(instance)
    print(ins.transient, ins.pending, ins.persistent, ins.deleted, ins.detached)
