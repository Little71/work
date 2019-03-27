import logging

logger = logging.getLogger(name=__name__)
logger.setLevel(logging.INFO)
logger.propagate = False #禁止向上传递

handler = logging.FileHandler(f'{basepath}:/{__name__}.log')
fmter = logging.Formatter('%(asctime)s [%(name)s %(funcName)s] %(message)s ')
handler.setFormatter(fmter)
logger.addHandler(handler)

#大数据实时处理技术