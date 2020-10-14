import rpyc

conn = rpyc.classic.connect("localhost")

rsys = conn.modules.sys

print(rsys.argv)

print(rpyc.__version__)