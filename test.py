import sys, struct, os, io, csv
from pprint import pprint
import numpy as np

pos = 0

types = {
    b'moov': (0, True),
    b'trak': (0, True),
    b'mdia': (0, True),
    b'minf': (0, True),
    b'stbl': (0, True),
}

ftyp_template = b'\x00\x00\x00\x14ftypmp41 \x13\x10\x18mp41'

meta_trak_template = b'\x00\x00\x01\xcatrak\x00\x00\x00\\tkhd\x00\x00\x00\x0f\xd9\x92\xf0n\xd9\x92\
\xf0n\x00\x00\x00\x04\x00\x00\x00\x00\x00\x0b\xe9\xec\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00@\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01fmdia\
\x00\x00\x00 mdhd\x00\x00\x00\x00\xd9\x92\xf0n\xd9\x92\xf0n\x00\x00\x03\xe8\
\x00\x002\xd5\x00\x00\x00\x00\x00\x00\x00*hdlr\x00\x00\x00\x00mhlrmeta\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\tGoPro MET\x00\x00\x01\x14minf\
\x00\x00\x00,gmhd\x00\x00\x00\x18gmin\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x0cgpmd\x00\x00\x00\x00\x00\x00\
\x00$dinf\x00\x00\x00\x1cdref\x00\x00\x00\x00\x00\x00\x00\x01\x00\x00\x00\
\x0calis\x00\x00\x00\x01\x00\x00\x00\xbcstbl\x00\x00\x00$stsd\x00\x00\x00\
\x00\x00\x00\x00\x01\x00\x00\x00\x14gpmd\x00\x00\x00\x00\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x18stts\x00\x00\x00\x00\x00\x00\x00\x01\x00\
\x00\x00\r\x00\x00\x03\xe9\x00\x00\x00\x1cstsc\x00\x00\x00\x00\x00\x00\x00\
\x01\x00\x00\x00\x01\x00\x00\x00\r\x00\x00\x00\x01\x00\x00\x00Hstsz\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\x00\x00\x108\x00\x00\x10\xc4\x00\
\x00\x10\xc0\x00\x00\x10\x80\x00\x00\x10\xc4\x00\x00\x10\x80\x00\x00\x10\
\xc0\x00\x00\x10\x80\x00\x00\x10\xc4\x00\x00\x10\x80\x00\x00\x10\xc0\x00\
\x00\x10\x80\x00\x00\x10\xc4\x00\x00\x00\x14stco\x00\x00\x00\x00\x00\x00\
\x00\x01\x00\x00\x00\x1c'

udta_template = b'\x00\x00\x00\x1efree\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x17FIRMHD5.03.02.51.00\x00\x00\x008LENSNAH6091100306860\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x18CAME\
\x8f\xfd \xb0\xcf\x1db/*j\xbb\x18\x90\xa1\x00j\x00\x00\x00\x14SETT\xc2\x00\
\x00\x00\x00\x00Ic\x00\x00\x00\x00\x00\x00\x00\x80AMBA\x00\x04\x00\x03\x01\
\x01x\x00\x00\x00\x00\x02\x00\x00:\xa7\x00\n\xfc\x80\x01\xc9\xc3\x80\x01\xc9\
\xc3\x80\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\t\x01\x01\x00\
\x00\x00(MUID\x8f\xfd \xb0\xcf\x1db/*j\xbb\x18\x90\xa1\x00j\x07\xe3\x90\x90\
\x00\x00\x03\xa6\x0c\xa1\x00\x00\x00\x00\x00\x00\x00\x00\x01\x9cHMMT\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00,BCID0\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x18GUMIs\xd3]X\xca\xc6\xd0%\xd5z\xbd\x00?\
\xe32\xd7\x00\x00\x00\x84free\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

mdat_meta_template = b'GPRO,\x01\x00\x00HD5.03.02.51.00NAH6091100306860\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x8f\xfd \xb0\xcf\
\x1db/*j\xbb\x18\x90\xa1\x00jC3211334576580\x00HERO5 Session\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\xc2cI\x00\x00\x8f\xfd \xb0\xcf\x1db/*j\xbb\x18\x90\xa1\x00j\x90\x90\xe3\
\x07\xa6\x03\x00\x00\x00\x00\xa1\x0c\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x01\x00\x00\x00`\xea\x00\x00\x80\x07\x00\x008\x04\x00\
\x00\x00\x00\x00\x00\x80\x07\x00\x008\x04\x00\x00\x01\x00\x00\x00\x80\xbb\
\x00\x00d\x00\x00\x00\x10\x00\x00\x00\x02\x00\x00\x00\x00\xf4\x01\x00\
\xee?m]n\xe4\x00\x00w\x02\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00GP\x03\x01\x00\x08\xa4\xe1\x00\x00\x03\
\xe9\x00\x00\x00\x00\x00\x00\x006\'d\x00*\xac4\xc8\x07\x80"~\\\x05\xb8\x08\
\x08\n\x00\x00\x07\xd2\x00\x03\xa9\x81\xd0\xc0\x00U\xd4\x80\x00\x15u)w\x97\
\x1a\x18\x00\n\xba\x90\x00\x02\xae\xa5.\xf2\xe1\xf0\x88E\x16\x00\x00\x00\x01\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x04(\xee80\x00\x00\x00\x01\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\
\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

#udta_template = b'abcd'

def parse_box_header(f):
    pos = f.tell()
    buf = f.read(8)
    f.seek(pos)
    return struct.unpack('>I4s', buf)

def read_box_data(f, size):
    pos = f.tell()
    f.seek(pos + 8)
    buf = f.read(size)
    f.seek(pos)
    return buf

def find_box(f, fourcc):
    while True:
        size, fourcc2 = parse_box_header(f)
        if fourcc2 == fourcc:
            return size
        f.seek(f.tell() + size)
        
def skip_box(f):
    size, _ = parse_box_header(f)
    f.seek(f.tell() + size)


def parse_box(f, until=None):
    pos = f.tell()
    if until and pos >= until:
        return False

    size, fourcc = parse_box_header(f)
    #print(pos, size, fourcc)

    if fourcc in types:
        head_size, has_children = types[fourcc]
        
        head = b''
        if head_size:
            head = read_box_data(f, head_size)

        ret = [fourcc, head, []]

        if has_children:
            f.seek(pos + 8 + head_size)
            children = ret[2]
            while True:
                child = parse_box(f, pos + size)
                if child:
                    children.append(child)
                else:
                    break
    else:
        data = read_box_data(f, size - 8)
        ret = [fourcc, data, []]
    
    f.seek(pos + size)
    return ret


def parse_file(f):
    boxes = []
    try:
        while True:
            boxes.append( parse_box(f) )
    except:pass
    return boxes



def flatten_box(box):
    data = box[1] # head
    
    for child in box[2]:
        data += flatten_box(child)

    buf = struct.pack('>I4s', 8 + len(data), box[0]) + data
    #print ('flattening', box[0], len(box[1]), len(buf))
    return buf


def walk_box(box, func, parent=None, index=None):
    func(box, parent, index)
    for i, child_box in enumerate(box[2]):
        walk_box(child_box, func, box, i)


def make_gpmf_klv(fourcc, typ, size, data):
    repeat = int(len(data) / size)
    fourcc, typ = map(lambda s: s.encode('ascii'), (fourcc, typ))
    if type(data) is str:
        data = data.encode('ascii')
    buf = struct.pack(">4scBH", fourcc, typ, size, repeat)
    buf += data
    buf += ((4 - len(data) % 4) % 4) * b'\x00' # pad to 32bit boundary

    return buf

def make_gpmf_payload(gyro, accl, tick):
    SCALE_GYRO = 3755
    SCALE_ACCL = 418

    def transform_vectors(vectors, scale):
        # gopro hero/session 5 axis order is Z, X, Y
        #vectors = [ int(c*scale) for v in vectors for c in (v[2], v[0], v[1])]
        vectors = [ int(c*scale) for v in vectors for c in (v[2], v[1], -v[0])]
        #vectors = [ int(c*scale) for v in vectors for c in v]
        vectors = b''.join(map(lambda x: struct.pack('>h', x), vectors))
        return vectors
    

    #print(gyro)
    
    gyro = transform_vectors(gyro, SCALE_GYRO)
    accl = transform_vectors(accl, SCALE_ACCL)

    
    gyro_stream = make_gpmf_klv('STRM', '\x00', 1, 
            make_gpmf_klv('STNM', 'c', 1, 'Gyroscope (z,x,y)')
            + make_gpmf_klv('SIUN', 'c', 1, 'rad/s')
            + make_gpmf_klv('SCAL', 's', 2, struct.pack('>h', SCALE_GYRO))
            + make_gpmf_klv('GYRO', 's', 6, gyro))
    
    accl_stream = make_gpmf_klv('STRM', '\x00', 1, 
        make_gpmf_klv('STNM', 'c', 1, 'Accelerometer (up/down, right/left, forward/back)')
        #+ make_gpmf_klv('TICK', 'L', 4, struct.pack('>I', tick))
        + make_gpmf_klv('SIUN', 'c', 1, b'm/s\xB2')
        + make_gpmf_klv('SCAL', 's', 2, struct.pack('>h', SCALE_ACCL))
        + make_gpmf_klv('ACCL', 's', 6, accl))

    return make_gpmf_klv('DEVC', '\x00', 1, 
          make_gpmf_klv('DVID', 'L', 1, struct.pack('>I', 1))
        + make_gpmf_klv('DVNM', 'c', 1, 'Camera')
        + accl_stream
        + gyro_stream
        )

def make_gpmf(gyro, accl):
    def chunker(seq, size):
        return (seq[pos:pos + size] for pos in range(0, len(seq), size))
    gyros = chunker(gyro, 400)
   # accls = chunker(accl, 200)
    t = 0
    buf = []
    for i, g in enumerate(gyros):
        buf.append(make_gpmf_payload(g, [[9.8, 0, 0]]*int(len(g)/2), 1000*t))
        t += 1001
    return buf

    

def get_values(f, typ, scale):
    f.seek(0)
    typ = typ.encode('ascii')
    #pos = 0
    vals = []
    while True:
        pos = f.tell()
        buf = f.read(4)
        if not buf:
            break

        if buf == typ:
            print(typ)
            t, size, repeat = struct.unpack('>cbh', f.read(4))
            data = f.read(size*repeat)
            data = struct.unpack('>{}h'.format( len(data)//2 ), data)
            data = map(lambda x: x/float(scale), data)
            vals += list( zip(*[iter(data)] * 3) )
        #else:
        f.seek(pos+1)

    return vals
                
def split_gpmf(f):
    f.seek(0)
    chunks = []
    buf = b''
    while True:
        b = f.read(4)
        
        if not b or b == b'DEVC' and len(buf) > 0:
            chunks.append(buf)
            if not b:
                break
            buf = b''
        buf += b
    return chunks


def read_log(f, camera_angle):
    reader = csv.reader(f)
    ca_rad = camera_angle*np.pi/180
    sn = np.sin(ca_rad)
    cs = np.cos(ca_rad)
    rot=np.array([[cs, 0, -sn], [0, 1, 0], [sn, 0, cs]])
    time_index = None
    gyro_index = None
    time_at_arm = None
    t = []
    gyro = []
    for row in reader:
        if not gyro_index and len(row) > 2:
            # read the positions of the columns of interest
            time_index = row.index('time') # should be 1
            gyro_index = row.index('gyroADC[0]')
        elif gyro_index:
            tm = float(row[time_index]) / 1e6 # usec to sec
            if time_at_arm is None:
                time_at_arm = tm
            t.append(tm - time_at_arm)
            gyros = tuple(map(lambda x: float(x)*np.pi/180, row[gyro_index:gyro_index+3]))
            #gyros = tuple(map(lambda x: float(x), row[gyro_index:gyro_index+3]))
            gyros = np.matmul(rot, gyros)
            # degrees/sec to rad/sec
            gyro.append(gyros)
    #print(gyro[-1])
    gyro.insert(0, (0,0,0))
    gyro.append((0,0,0))
    t.insert(0, t[0]-.0001)
    t.append(t[-1]+.0001)
    return np.array(t), np.array(gyro)

def map_time(t, offset1, time1=None, offset2=None, time2=None):
    if time2 is None:
        a = 0
        b = offset1
    else:
        a = (offset2 - offset1)/(time2 - time1)
        b = offset1 - a*time1

    t = t + a*t + b

    return t

def map_gyro(t, gyro, video_length):
    vt = np.linspace(0, video_length, int(video_length*400))
    return np.transpose(np.array([ np.interp(vt, t, gyro_axis) for gyro_axis in np.transpose(gyro) ])), vt
    

fm = open('meta', 'rb')
gpmf_chunks = split_gpmf(fm)
#print ( sum(map(len, gpmf_chunks)))
#print(gpmf_chunks[1][:10])
#sys.exit()
if 0:
    # make 
    fmeta = open(sys.argv[1], 'rb')
    fin = open(sys.argv[2], 'rb')
    fout = open(sys.argv[3], 'wb')

    meta = parse_file(fmeta)

    fout.write(ftyp_template)

    find_box(fin, b'moov')
    mdat_end = fin.tell()
    moov = parse_box(fin)
    del moov[2][1]
    del moov[2][-2:]
    print(moov)
    #fout.write(flatten_box(moov))
    fin.seek(0)
    mdat_size = find_box(fin, b'mdat') - 8
    fin.seek(8, os.SEEK_CUR)

    fout.write(struct.pack('>I', mdat_size + 8) + b'mdat')
    
    while mdat_size:
        chunk_size = min(mdat_size, int(10e6))
        fout.write(fin.read(chunk_size))
        mdat_size -= chunk_size

    fout.write(flatten_box(moov))

if 0:
    fmeta = open(sys.argv[1], 'rb')
    fin = open(sys.argv[2], 'rb')
    fout = open(sys.argv[3], 'wb')

    meta = parse_file(fmeta)
    gpmf_size = len(meta[1][1])

    fout.write(ftyp_template)

    find_box(fin, b'moov')
    mdat_end = fin.tell()
    moov = parse_box(fin)
    fin.seek(0)

    mdat_size = find_box(fin, b'mdat') - 8
    fin.seek(8, os.SEEK_CUR)

    fout.write(struct.pack('>I', mdat_size + 8 + gpmf_size) + b'mdat')
    
    
    while mdat_size:
        chunk_size = min(mdat_size, int(10e6))
        fout.write(fin.read(chunk_size))
        mdat_size -= chunk_size

    meta_pos = fout.tell()
    fout.write(meta[1][1])

    moov[2].insert(1, [b'udta', udta_template])
    meta_track = meta[2][2][-1]
    stco = meta_track[2][-1][2][-1][2][-1][2][-1]
    stco[1] = stco[1][:-4] + struct.pack('>I', meta_pos)
    moov[2].append(meta_track)
    

    fout.write(flatten_box(moov))
if 0:
    flog = open('LOG.csv')
    t, gyro = read_log(flog, 30)
    t = map_time(t, -130.143)
    gyro = map_gyro(t, gyro, 13.3)
    print(gyro)
if 1:
    if 0:
        f = open('meta', 'rb')
        accl = np.array(get_values(f, 'ACCL', 418) )
        gyro = np.array(get_values(f, 'GYRO', 3755) )
        print (len(gyro))
        accl_x = np.linspace(0, 1, len(accl))
        gyro_x = np.linspace(0, 1, len(gyro))
        target_accl_x = np.linspace(0, 1, 5205/2)
        target_gyro_x = np.linspace(0, 1, 5205)
        
        accl = np.array([ np.interp(target_accl_x, accl_x, ac) for ac in np.transpose(accl) ])
        accl = np.transpose(accl)
        
        gyro = np.array([ np.interp(target_gyro_x, gyro_x, gy) for gy in np.transpose(gyro) ])
        gyro = np.transpose(gyro)
        
        gpmf_data = make_gpmf(gyro, accl)
        #gpmf_data = gpmf_chunks
    else:
        flog = open(sys.argv[1])
        t, gyro = read_log(flog, -30)
        #t = map_time(t, -130.143)#3.067)
        #gyro, t = map_gyro(t, gyro, 13.3)#39.54)
        #t = map_time(t, -99.875) # nove2
        t = map_time(t, -120) # nove3
        #gyro, t = map_gyro(t, gyro, 42.592) # nove2
        gyro, t = map_gyro(t, gyro, 9.31) # nove3
        #np.savetxt('gyro1.csv', np.concatenate((t.reshape(t.size,1), gyro), 1))
        gpmf_data = make_gpmf(gyro, None)



    #fmeta = open(sys.argv[1], 'rb')
    fin = open(sys.argv[2], 'rb')
    fout = open(sys.argv[3], 'wb')

    fm = io.BytesIO(meta_trak_template)
    meta_track = parse_box(fm)

    gpmf_bin = b''.join(gpmf_data)
    gpmf_size = len(gpmf_bin)

    fout.write(ftyp_template)

    find_box(fin, b'moov')
    mdat_end = fin.tell()
    moov = parse_box(fin)
    fin.seek(0)

    mdat_size = find_box(fin, b'mdat') - 8
    in_mdat_offset = fin.tell()
    out_mdat_offset = fout.tell() + len(mdat_meta_template)
    fin.seek(8, os.SEEK_CUR)

    fout.write(struct.pack('>I', mdat_size + 8 + gpmf_size + len(mdat_meta_template)) + b'mdat')
    fout.write(mdat_meta_template)
    
    
    while mdat_size:
        chunk_size = min(mdat_size, int(10e6))
        fout.write(fin.read(chunk_size))
        mdat_size -= chunk_size

    meta_pos = fout.tell()
    fout.write(gpmf_bin)

    def relocate_stco(box, parent, index):
        if box[0] == b'stco':
            count = struct.unpack('>I', box[1][4:8])[0]
            offset_format = '>{}I'.format(count)
            offsets = struct.unpack(offset_format, box[1][8:])
            # translate offsets to new origin
            offsets = [o - in_mdat_offset + out_mdat_offset for o in offsets]
            box[1] = box[1][:8] + struct.pack(offset_format, *offsets)
    walk_box(moov, relocate_stco)

    def delete_udta(box, parent, index):
        if box[0] == b'udta':
            del parent[2][index]
            raise StopIteration
    try:
        walk_box(moov, delete_udta)
    except StopIteration: pass

    for_delete = []
    def delete(box, parent, index):
        if box[0] in (b'tref', b'iods'):
            for_delete.append( (parent, index) )
    #walk_box(moov, delete)
    for parent, index in for_delete:
        del parent[2][index]

    moov[2].insert(1, [b'udta', udta_template, []])

    # time to sample
    stts = meta_track[2][-1][2][-1][2][-1][2][1]
    stts[1] = struct.pack('>4I', 0, 1, len(gpmf_data), 1)

    # chunks. There's only one chunk
    stsc = meta_track[2][-1][2][-1][2][-1][2][2]
    stsc[1] = struct.pack('>5I', 0, 1, 1, len(gpmf_data), 1)
    stsc[1] = struct.pack('>5I', 0, 1, 1, 1, 1)

    # sample sizes
    stsz = meta_track[2][-1][2][-1][2][-1][2][3]
    stsz[1] = struct.pack('>{}I'.format(3 + len(gpmf_data)), *[0, 0, len(gpmf_data)] + list(map(len, gpmf_data)))

    # position of the chunk in the file
    stco = meta_track[2][-1][2][-1][2][-1][2][4]
    stco[1] = stco[1][:-4] + struct.pack('>I', meta_pos)
    
    chunk_offset = meta_pos
    chunk_offsets = []
    for l in map(len, gpmf_data):
        chunk_offsets.append(chunk_offset)
        chunk_offset += l
    stco[1] = struct.pack('>{}I'.format(2 + len(gpmf_data)), *[0, len(gpmf_data)] + chunk_offsets)
    
    

    moov[2].append(meta_track)
    

    fout.write(flatten_box(moov))

#pprint(map(lambda x:x[0], parse_file(fmeta)))
#meta = parse_box()
#find_box(f, 'mdat')
#skip_box(f)
#find_box(f, 'moov')
#moov = parse_box(f)
#moov[2] = [moov[2][0], moov[2][-1]]
#pprint.pprint (moov)
#flat=flatten_box(moov)

#out = open('tmp', 'wb')
#out.write(flat)
#print (flatten_box(moov))

#f = open('meta', 'rb')
#print(len( get_values(f, 'ACCL', 418) ))
#print( len(get_values(f, 'GYRO', 3755) ))

#print (repr(make_gpmf_payload([(0, 0, 0), (1,0,0), (2, 0, 0)], [(1, 2, 3), (4,5,6)])))

#fm = io.BytesIO(meta_trak_template)
#meta = parse_box(fm)
#print(meta)