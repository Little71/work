import json
import logging

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, String, BigInteger, Boolean, Text
from sqlalchemy import Column, ForeignKey, create_engine, UniqueConstraint, PrimaryKeyConstraint
from sqlalchemy.orm import sessionmaker, relationship

from pipeline import config
from .state import *

Base = declarative_base()


# schema定义

class Graph(Base):
    __tablename__ = 'graph'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=False, unique=True)
    desc = Column(String(500), nullable=False)
    checked = Column(Integer, nullable=False, default=0)
    sealed = Column(Integer, nullable=False, default=0)

    # 经常从图查看所有顶点、边的信息
    vertexs = relationship('Vertex')
    edges = relationship('Edge')


# 顶点表
class Vertex(Base):
    __tablename__ = 'vertex'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(48), nullable=True)
    input = Column(Text, nullable=False)  # 输入参数
    script = Column(Text, nullable=False)
    g_id = Column(Integer, ForeignKey('graph.id'), nullable=False)

    # 这里不写因为上面外键指定了，所以关系就确定了，即一对一的关系
    graph = relationship('Graph')

    # 从顶点查看他的边，这里必须使用foreign_keys，其值必须使用引号，多个用逗号或者空格分割
    # 有括号或者没有括号都可以
    # 如另一张表有当前表的同一个字段表示的两个外键的意思，在当前表查看其它两个外键就需要区分
    # 所以查询回来会有很多个结果，所以加个复数
    tails = relationship('Edge', foreign_keys='[Edge.tail]')
    heads = relationship('Edge', foreign_keys='Edge.head')


class Edge(Base):
    __tablename__ = 'edge'

    id = Column(Integer, primary_key=True, autoincrement=True)
    g_id = Column(Integer, ForeignKey('graph.id'), nullable=False)
    tail = Column(Integer, ForeignKey('vertex.id'), nullable=False)
    head = Column(Integer, ForeignKey('vertex.id'), nullable=False)


# engine，辅助表

# pipeline
class Pipeline(Base):
    __tablename__ = 'pipeline'

    id = Column(Integer, primary_key=True, autoincrement=True)
    state = Column(Integer, nullable=False, default=STATE_WAITING)
    g_id = Column(Integer, ForeignKey('graph.id'), nullable=False)
    current = Column(Integer, ForeignKey('vertex.id'), nullable=False)

    vertex = relationship('Vertex')


class Track(Base):
    __tablename__ = 'track'

    id = Column(Integer, primary_key=True, autoincrement=True)
    p_id = Column(Integer, ForeignKey('pipeline.id'), nullable=False)
    v_id = Column(Integer, ForeignKey('vertex.id'), nullable=False)
    state = Column(Integer, nullable=False, default=STATE_WAITING)
    input = Column(Text, nullable=False)
    output = Column(Text, nullable=False)

    vertex = relationship('Vertex')
    pipeline = relationship('Pipeline')


# 封装数据库引擎、会话到类中，实现多例模式

class DateBase:

    def __init__(self):
        self._engine = None
        self._session = None
        self._is_inited = False  # 初始化标记

    def init_db(self, connstr: str, **kwargs):
        if not self._is_inited:
            self._engine = create_engine(connstr, **kwargs)
            self._session = sessionmaker(bind=self._engine)()
            self._is_inited = True
        return self

    def createalltables(self, tables=None):
        Base.metadata.create_all(self._engine, tables)

    def dropalltables(self):
        Base.metadata.drop_all(self._engine)

    @property
    def session(self):
        if not self._is_inited:
            raise AttributeError('Not initialized.')
        return self._session

    @property
    def engine(self):
        if not self._is_inited:
            raise AttributeError('Not initialized.')
        return self._engine


db = DateBase().init_db(connstr=config.SQLURL, encoding=config.ENCODING, echo=config.SQLDEBUG)
