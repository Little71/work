import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from json import JSONDecodeError

from pipeline.models import Graph, db, Vertex, Edge, Pipeline, Track
from functools import wraps

from .state import *


# 因为是service层，是提供接口给别人用，所以把异常抛出去，然后记录下日志，然后在应用层处理这个异常
def transactional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ret = fn(*args, **kwargs)
        try:
            db.session.commit()
            return ret
        except Exception as e:
            db.session.rollabck()
            # +日志输出
            raise e

    return wrapper


@transactional
def create_graph(name, desc=None):
    g = Graph()
    g.name = name
    g.desc = desc
    db.session.add(g)
    return g


@transactional
def add_vertex(graph: Graph, name: str, input=None, script=None):
    v = Vertex()
    v.g_id = graph.id
    v.name = name
    v.input = input
    try:
        json.loads(script)
        v.script = script
    except JSONDecodeError:
        v.script = {'script': f'{script}'}
    db.session.add(v)
    return v


@transactional
def add_edge(graph: Graph, tail: Vertex, head: Vertex):
    e = Edge()
    e.g_id = graph.id
    e.tail = tail
    e.head = head
    db.session.add(e)
    return e


# 找到顶点，在去找对应的边，在删除
def del_vertex(id):
    query = db.session.query(Vertex).filter(Vertex.id == id)
    v = query.first()
    if v:
        try:
            db.session.query(Edge).filter((Edge.tail == v.id) | (Edge.head == v.id)).delete()
            query.delete()
            db.session.commit()
        except Exception as e:
            db.session.rollabck()
            raise e
    return v


# 上面只是增加的实现，还有修、查、删

# 测试数据
def test_create_dag():
    try:
        g = create_graph('test')
        # 增加顶点
        input = """
        {
            "ip":{
                "type":"srt",
                "required":"true",
                "default":192.168.0.100
            }
        }
        """
        script = {
            'script': 'echo test.A',
            'next': 'B'
        }
        # 这里为了用户方便，next可以接受两种类型，数字表示顶点id，字符串表示DAG的顶点，不能重复

        # 添加顶点
        # next顶点验证可以在定义，也可以在使用时，即这个顶点有没有
        a = add_vertex(g, 'A', None, json.dumps(script))
        b = add_vertex(g, 'B', None, 'echo B')
        c = add_vertex(g, 'C', None, 'echo C')
        d = add_vertex(g, 'D', None, 'echo D')

        # 增加边
        ab = add_edge(g, a, b)
        ac = add_edge(g, a, c)
        cb = add_edge(g, c, b)
        bd = add_edge(g, b, d)

        # 创建环路
        g = create_graph('test2')  # 环路

        a = add_vertex(g, 'A', None, 'echo A')
        b = add_vertex(g, 'B', None, 'echo B')
        c = add_vertex(g, 'C', None, 'echo C')
        d = add_vertex(g, 'D', None, 'echo D')

        # 增加边
        ba = add_edge(g, b, a)
        ac = add_edge(g, a, c)
        cb = add_edge(g, c, b)
        bd = add_edge(g, b, d)

        # 创建DAG
        g = create_graph('test3')  # 多个终点

        a = add_vertex(g, 'A', None, 'echo A')
        b = add_vertex(g, 'B', None, 'echo B')
        c = add_vertex(g, 'C', None, 'echo C')
        d = add_vertex(g, 'D', None, 'echo D')

        # 增加边
        ba = add_edge(g, b, a)
        ac = add_edge(g, a, c)
        bc = add_edge(g, b, c)
        bd = add_edge(g, b, d)

        g = create_graph('test3')  # 多个起点

        a = add_vertex(g, 'A', None, 'echo A')
        b = add_vertex(g, 'B', None, 'echo B')
        c = add_vertex(g, 'C', None, 'echo C')
        d = add_vertex(g, 'D', None, 'echo D')

        # 增加边
        ab = add_edge(g, a, b)
        ac = add_edge(g, a, c)
        cb = add_edge(g, c, b)
        bd = add_edge(g, b, d)

    except:
        pass


def check_graph(graph: Graph) -> bool:
    '''验证是否是一个合法的DAG'''
    # 反正都要遍历所欲的顶点和边，不如一次性把所属有的顶点和边都查出来，在内存中反复遍历
    query = db.session.query(Vertex).filter(Vertex.g_id == graph.id)
    vertexes = [vertex.id for vertex in query]
    query = db.session.query(Edge).filter(Edge.g_id == graph.id)
    edges = [(dege.tail, dege.head) for dege in query]

    while True:
        vis = []  # 就放一个索引
        for i, v in enumerate(vertexes):
            for _, h in edges:
                if h == v:
                    break
            else:  # 没有break，说明遍历一遍，没有找到该顶点作为弧头，即入度为0
                ejs = []
                # 然后再去找这个顶点作为弧尾
                for j, (t, _) in enumerate(edges):
                    if t == v:
                        ejs.append(j)
                vis.append(i)
                # 逆向，从后面开始删除，不然从前面开始删除，后面的索引就改变了
                for j in reversed(ejs):
                    edges.pop(j)
                break
                # 一旦找到入度为0的顶点，就需要从列表中删除，列表重新遍历
        else:
            return False
        for i in vis:
            vertexes.pop(i)
        print(vertexes, edges)
        if len(vertexes) + len(edges) == 0:
            # 验证通过，修改checked为1
            try:
                graph = db.session.query(Graph).filter(Graph.id == graph.id).first()
                if graph:
                    graph.checked = 1
                db.session.add(graph)
                db.session.commit()
                return True
            except Exception as e:
                db.session.rollabck()
                raise e


# 开启一个流程，用户指定一个起点（入度为0）
@transactional
def start(graph: Graph, vertex: Vertex, params=None):
    # 判断流程是否存在，且checked为1即校验通过
    g = db.session.query(Graph).filter(Graph.id == graph.id).filter(Graph.checked == 1).first()
    if not g:
        return
    # 顶点id是用户选择好的起点id，必须属于这个graph的
    # 可以在做一次该顶点是否入度为0的验证，因为客户端发来的数据不可信
    v = db.session.query(Vertex).filter((Vertex.g_id == vertex.id) & (Vertex.g_id == graph.id)).first()
    if not v:
        return

    # 写入pipelive表
    p = Pipeline()
    p.current = v.id
    p.g_id = g.id
    p.state = STATE_WAITING
    db.session.add(p)

    # 写入track表
    t = Track()
    t.p_id = p.id
    t.state = STATE_WAITING
    t.pipeline = p
    db.session.add(t)

    # 标记有人使用过了，sealed
    if g.sealed == 0:
        g.sealed = 1
        db.session.add(g)
    return p


# 测试start
def test_start():
    g = Graph()
    g.id = 1
    v = Vertex()
    v.id = 1
    p = start(g, v)
    if p:
        print(p)
        print(p.vertex.script)


# input校验函数
def check_input_params() -> bool:
    return {}  # 返回空字典，说明没有设定input


#######
# 执行器
from subprocess import Popen, PIPE


def execute(script, timeout=None):
    proc = Popen(script, shell=True, stdout=PIPE)
    code = proc.wait(timeout)
    txt = proc.stdout.read()
    return code, txt


# 流转
# 线程中执行

MAX_POOL_SIZE = 5
executor = ThreadPoolExecutor(max_workers=MAX_POOL_SIZE)


def iter_pipelines():
    yield from (db.session.query(Pipeline).filter(Pipeline.state == STATE_WAITING))
    # query = db.session.query(Pipeline).filter(Pipeline.state == STATE_WAITING)
    # pipelines = query.all()
    # for pipeline in pipelines:
    #     yield pipeline

@transactional
def find_next_id(p:Pipeline,query):
    edge = query.first()
    if edge:
        p.current = edge.head
        p.state = STATE_WAITING
        db.session.add(p)

        t = Track()
        t.p_id = p.id
        t.v_id = edge.head
        t.state = STATE_WAITING
        db.session.add(t)
        return edge.head
    else:
        p.state = STATE_FINISH
        db.session.add(p)

# 流转
# 注意目前一次只处理一段pipeline表中状态为wating的，异步的
@transactional
def shift():
    futures = {}
    with executor:
        for pipeline in iter_pipelines():
            s = json.loads(pipeline.vertex.script)
            script = s['script']
            f = executor.submit(execute, script)
            futures[f] = pipeline, s

        for f in as_completed(futures):
            p, s = futures[f]
            try:
                code, txt = f.result()
                if code == 0:
                    # 脚本正常 track记录 output  找不到抛异常
                    t = db.session.query(Track).filter((Track.p_id == p.id) & (Track.v_id == p.current)).one()
                    t.state = STATE_SUCCEED
                    t.output = txt
                    db.session.add(t)
                    # 如果当前节点是重点，就不用到下一个节点，
                    # 修改pipeline、track状态为finish就行了，判断当前顶点的出度是否为0

                    # 寻找下一个执行节点vertex，找到就修改
                    # 如果是自动，就要在script中增加些参数，直接将current更新为下一个节点，状态为waiting
                    if 'next' in s:
                        n = s['next']
                        # 验证是否是下一个节点，成功返回下一个顶点id
                        if type(n) == int:
                            query = db.session.query(Edge).filter((Edge.tail == p.current) & (Edge.head == n))
                        else:
                            vertex = db.session.query(Vertex).filter((Vertex.name == n) & (Vertex.g_id == p.g_id)).first()
                            query = db.session.query(Edge).filter((Edge.tail == p.current) & (Edge.head == vertex.id))
                        next_id = find_next_id(p, query)
                        return next_id
                    else:
                        # TODO 如果是手动，就把pipeline中的current状态置为state_succeed,以后还得提供便利状态为state_scuueed的顶点
                        p.state = STATE_SUCCEED
                        db.session.add(p)
                else:
                    pass
            except Exception as e:
                print(f'{e}')