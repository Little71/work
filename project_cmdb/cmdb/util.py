import logging


def getlogger(mod_name: str, filepath: str):
    logger = logging.getLogger(mod_name)
    logger.setLevel(logging.INFO)
    logger.propagate = False  # 禁止向上传递

    handler = logging.FileHandler(filepath)
    fmter = logging.Formatter('%(asctime)s %(module)s %(funcName)s %(message)s ')
    handler.setFormatter(fmter)
    logger.addHandler(handler)
    return logger


logger = getlogger(__name__,"xxx:/xxx.log")