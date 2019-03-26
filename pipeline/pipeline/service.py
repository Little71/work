import json

from pipeline.models import Graph, db, Vertex, Edge
from functools import wraps


# 因为是service层，是提供接口给别人用，所以把异常抛出去，然后记录下日志，然后在应用层处理这个异常
def transactional(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        ret = fn(*args, **kwargs)
        db.session.add(ret)
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
    return g


@transactional
def add_vertex(graph: Graph, name: str, input=None, script=None):
    v = Vertex()
    v.g_id = graph.id
    v.name = name
    v.input = input
    v.script = script
    return v


@transactional
def add_edge(graph: Graph, tail: Vertex, head: Vertex):
    e = Edge()
    e.g_id = graph.id
    e.tail = tail
    e.head = head
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
                #然后再去找这个顶点作为弧尾
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
