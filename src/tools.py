import sys


class EagerStream():
    '''A thin wrapper around I/O stream that immediately flushes the output.'''
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()
        sys.stderr.write(data)
        sys.stderr.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)
