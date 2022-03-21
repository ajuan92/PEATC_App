"""
MIT License

Copyright (c) 2017 Paul Genssler

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import array
import struct

__author__ = 'Paul Genssler'


def memory_write(dev_file: str, data: tuple):
    """!
    reads a byte from a rc2f memory file
    @param dev_file: the memory to use
    @param address: which byte to read
    @param data: a tuple of bytes to write
    """
    with open(dev_file, 'wb') as mem:
        mem.write(struct.pack('B' * len(data), *data))


def stream_write(dev_file: str, data) -> int:
    """!
    stream data into the device
    @param dev_file: the target device
    @param data: data to write, iterable and slicable
    container (like a list) with bytes objects
    @return: how many bytes were written
    @rtype: int
    """
    with open(dev_file, 'wb') as fifo:
        wrote = 0
        data_len = len(data)
        while data_len > wrote:
            wrote += fifo.write(data[wrote:data_len])
        return wrote


def memory_read(dev_file: str, length=1) -> tuple:
    """!
    reads bytes from a rc2f memory file
    @param dev_file: the memory to use
    @param length: how many bytes to read
    @return: the read bytes as a tuple
    @rtype: tuple
    """
    with open(dev_file, 'rb') as mem:
        data = mem.read(length)
        return struct.unpack('B' * length, data)


def stream_read(dev_file: str, length=2 ** 12, chunk_size=2 ** 12):
    """!
    reads data from the device into an array of chuck_size bytes and yields it
    @param dev_file: the target device
    @param length: how many bytes to read, -1 until eof
    @param chunk_size: how much data per read, low values impact performance
    """
    with open(dev_file, 'rb') as fifo:
        read = 0
        while length < 0 or read < length:
            data = array.array('B')
            try:
                data.fromfile(fifo, min(length - read, chunk_size))
                Checj = data
                yield Checj
                read += len(data)
            except EOFError:
                yield data
                break
