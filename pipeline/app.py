from pipeline.models import Graph
from pipeline.service import test_create_dag, check_graph

test_create_dag()

for i in range(1,5):
    g= Graph()
    g.id = i
    print(check_graph(g),'~~~~~~~~~~~~~')








