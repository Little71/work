from pipeline.models import Graph
from pipeline.service import test_create_dag, check_graph

# test_create_dag()
#
# for i in range(1, 5):
#     g = Graph()
#     g.id = i
#     print(check_graph(g), '~~~~~~~~~~~~~')

from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import threading


def test_func(s, key):
    print(f"enter~~{threading.current_thread()} {s}s key={key}")
    threading.Event().wait(s)
    return f"ok {threading.current_thread()}"


with ThreadPoolExecutor(max_workers=3) as executor:
    futures = {executor.submit(test_func, random.randint(1, 8), i): i for i in range(7)}
    for future in as_completed(futures):
        id = futures[future]
        try:
            print(id, future.result())

        except Exception as e:
            print(id, 'failed')
