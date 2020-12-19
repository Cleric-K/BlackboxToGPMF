import struct, codecs, pprint
import numpy as np

SCALE_GYRO = 3755
SCALE_ACCL = 418
GYRO_SAMPLES_PER_CHUNK = 400
CHUNK_TIME = 1.001

def klv(fourcc, typ, size, data):
    repeat = int(len(data) / size)
    fourcc, typ = map(lambda s: s.encode('ascii'), (fourcc, typ))
    if type(data) is str:
        data = data.encode('ascii')
    buf = struct.pack(">4scBH", fourcc, typ, size, repeat)
    buf += data
    buf += ((4 - len(data) % 4) & 0b11) * b'\x00' # pad to 32bit boundary

    return buf


def make_gpmf_payload(gyro, accl, tick, gyro_total, accl_total):
    def transform_vectors(vectors, scale):
        # gopro hero/session 5 axis order is Z, X, Y
        #vectors = [ int(c*scale) for v in vectors for c in (v[2], v[0], v[1])]
        vectors = [ int(c*scale) for v in vectors for c in (v[2], v[1], -v[0])]
        #vectors = [ int(c*scale) for v in vectors for c in v]
        vectors = np.clip(vectors, -32768, 32767)
        vectors = b''.join(map(lambda x: struct.pack('>h', x), vectors))
        return vectors
    

    #print(gyro)
    
    gyro = transform_vectors(gyro, SCALE_GYRO)
    accl = transform_vectors(accl, SCALE_ACCL)

    
    gyro_stream = klv('STRM', '\x00', 1, 
            klv('TSMP', 'L', 4, struct.pack('>I', gyro_total))
            + klv('TICK', 'L', 4, struct.pack('>I', tick))
            + klv('STNM', 'c', 1, 'Gyroscope (z,x,y)')
            + klv('SIUN', 'c', 1, 'rad/s')
            + klv('SCAL', 's', 2, struct.pack('>h', SCALE_GYRO))
            + klv('GYRO', 's', 6, gyro))
    
    accl_stream = klv('STRM', '\x00', 1, 
        klv('TSMP', 'L', 4, struct.pack('>I', accl_total))
        + klv('TICK', 'L', 4, struct.pack('>I', tick))
        + klv('STNM', 'c', 1, 'Accelerometer (up/down, right/left, forward/back)')
        + klv('SIUN', 'c', 1, b'm/s\xB2')
        + klv('SCAL', 's', 2, struct.pack('>h', SCALE_ACCL))
        + klv('ACCL', 's', 6, accl))

    shut_stream = klv('STRM', '\x00', 1, 
        #klv('TSMP', 'L', 4, struct.pack('>I', accl_total))
        klv('TICK', 'L', 4, struct.pack('>I', tick))
        + klv('STNM', 'c', 1, 'Exposure time (shutter speed)')
        + klv('SIUN', 'c', 1, b's')
        + klv('SHUT', 'f', 4, struct.pack('>30f', *[0.0036]*30)))

    return klv('DEVC', '\x00', 1, 
          klv('DVID', 'L', 1, struct.pack('>I', 1))
        + klv('DVNM', 'c', 1, 'Camera')
        + accl_stream
        + gyro_stream
        + shut_stream
        )

def make_gpmf(gyro):
    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))
    gyros = chunker(gyro, GYRO_SAMPLES_PER_CHUNK)

    buf = []
    gyro_total = 0
    accl_total = 0
    for i, g in enumerate(gyros):
        accl_len = int(len(g)/2)
        gyro_total += len(g)
        accl_total += accl_len
        buf.append(make_gpmf_payload(g, [[0, 0, 9.8]]*accl_len, 3490 + 1001*i, gyro_total, accl_total))
    return buf


class KLV:
    def __init__(self, key, type, size, repeat, data):
        self.key = key
        self.type = type
        self.size = size
        self.repeat = repeat
        self.data = data
        self.children = []

    def flatten(self):
        if self.children:
            data = b''.join(map(lambda ch: ch.flatten(), self.children))
            repeat = len(data)
        else:
            repeat = len(self.data) / self.size
            data = self.data + ((4 - len(self.data)%4) & 0b11)*b'\x00'

        return struct.pack('>4ssBH', self.key, self.type, self.size, self.repeat) + data

    def __repr__(self):
        r = 'KLV({}, type={}, size={}, repeat={}, {} bytes data'.format(codecs.decode(self.key, 'ascii'),
        repr(codecs.decode(self.type, 'ascii')), self.size, self.repeat,len(self.data))
        #print(lines)
        if self.children:
            lines = pprint.pformat(self.children).split('\n')
            lines = [ line if not i else '  ' + line for i, line in enumerate(lines)]
            lines = '\n'.join(lines)
            r += ', ' + lines
        r += ')'
        return r


def parse(buf):
    key, type, size, repeat = struct.unpack('>4ssBH', buf[:8])
    #print(key, type, size, repeat)
    data = buf[8:8 + size*repeat]
    klv = KLV(key, type, size, repeat, bytearray(data))
    if type == b'\x00':
        while data:
            data, child_klv = parse(data)
            klv.children.append(child_klv)
        return buf[8 + size*repeat:], klv
    else:
        bundary_len = 8 + size*repeat + ((4 - (size*repeat) % 4) & 0b11)
        #print('returning', bundary_len)
        return buf[bundary_len:], klv