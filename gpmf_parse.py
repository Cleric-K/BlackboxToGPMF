import gpmf

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
_fmeta = open('meta', 'rb')
gpmf_chunks = split_gpmf(_fmeta)

_, g = gpmf.parse(gpmf_chunks[0])
del g.children[-2:]
print(g)
print(g.flatten() == gpmf_chunks[0])