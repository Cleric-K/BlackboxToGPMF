import mp4
import sys, struct

f = open(sys.argv[1], 'rb')
mp4.find_atom(f, b'moov')
moov = mp4.parse_atom(f)

for trak in moov.find(b'trak'):
    if trak.find(b'gpmd'):
        meta_trak = trak
        break
else:
    sys.exit(1)

stsz = meta_trak.find(b'stsz')[0]
stco = meta_trak.find(b'stco')[0]

num_chunks = struct.unpack('>I', stsz.data[8:8+4])[0]
chunk_sizes = struct.unpack('>{}I'.format(num_chunks), stsz.data[12:])
chunk_offsets = struct.unpack('>{}I'.format(num_chunks), stco.data[8:])

buf = []
for offset, size in zip(chunk_offsets, chunk_sizes):
    f.seek(offset)
    buf.append(f.read(size))

fout = open(sys.argv[2], 'wb')
fout.write(b''.join(buf))
