import logging

g_log_m = None
g_log_s = None

def init_logger():
    global g_log_m
    global g_log_s

    logging.basicConfig(filename='nlp_server.log', encoding='utf-8', level=logging.DEBUG)

    g_log_m = logging.getLogger('MAIN')
    g_log_s = logging.getLogger("SCHED")

    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)
    ch.setFormatter(formatter)

    g_log_m.addHandler(ch)
    g_log_s.addHandler(ch)

def logger_main():
    global g_log_m
    return g_log_m

def logger_sched():
    global g_log_s
    return g_log_s


