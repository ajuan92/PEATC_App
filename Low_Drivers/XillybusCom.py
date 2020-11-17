import array
import struct


def memory_write(dev_file: str, data: tuple):

    with open(dev_file, 'wb') as mem:
        mem.write(struct.pack('B' * len(data), *data))


def stream_write(dev_file: str, data) -> int:

    with open(dev_file, 'wb') as fifo:
        wrote = 0
        data_len = len(data)
        while data_len > wrote:
            wrote += fifo.write(data[wrote:data_len])
        return wrote

def memory_read(dev_file: str, length=1) -> tuple:

    with open(dev_file, 'rb') as mem:
        data = mem.read(length)
        return struct.unpack('B' * length, data)


def stream_read(dev_file: str, length=-1, chunk_size=2 ** 12):

    with open(dev_file, 'rb') as fifo:
        read = 0
        while length < 0 or read < length:
            data = array.array('b')
            try:
                yield data.fromfile(fifo, min(length - read, chunk_size))
                read += len(data)
            except EOFError:
                yield data
                break
