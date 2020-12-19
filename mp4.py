import struct, codecs, pprint

'''
    https://developer.apple.com/standards/qtff-2001.pdf
    https://sourceforge.net/projects/mp4-inspector/
'''

ATOM_HEAD_SIZE = 8

types = {
    b'moov': (0, True),
    b'trak': (0, True),
    b'mdia': (0, True),
    b'minf': (0, True),
    b'stbl': (0, True),
    b'gmhd': (0, True),
}

class Atom:
    def __init__(self, key, data):
        self.key = key
        self.data = bytearray(data)
        self.children = []

    def walk(self, func, parent=None, index=None):
        func(self, parent, index)
        for i, child in enumerate(self.children):
            ret = child.walk(func, self, i)
            if ret is False:
                return False

    def find(self, key):
        atoms = []
        
        def finder(atom, parent, index):
            if atom.key == key:
                atoms.append(atom)

        self.walk(finder)

        return atoms

    def delete_child(self, func):
        for i, ch in enumerate(self.children):
            if func(ch):
                del self.children[i]
                return

    def flatten(self):
        data = bytearray(self.data) # head
    
        for child in self.children:
            data += child.flatten()

        buf = atom_head(self.key, ATOM_HEAD_SIZE + len(data)) + data
        return buf

    def __repr__(self):
        r = 'Atom({}, {} bytes data'.format(codecs.decode(self.key, 'ascii'), len(self.data))
        #print(lines)
        if self.children:
            lines = pprint.pformat(self.children).split('\n')
            lines = [ line if not i else '  ' + line for i, line in enumerate(lines)]
            lines = '\n'.join(lines)
            r += ', ' + lines
        r += ')'
        return r

def atom_head(key, size):
    return struct.pack('>I4s', size, key)

def peek_header(f):
    pos = f.tell()
    buf = f.read(ATOM_HEAD_SIZE)
    f.seek(pos)
    return struct.unpack('>I4s', buf)

def read_data(f, size):
    pos = f.tell()
    f.seek(pos + ATOM_HEAD_SIZE)
    buf = f.read(size)
    f.seek(pos + ATOM_HEAD_SIZE + size)
    return buf

def find_atom(f, fourcc):
    while True:
        size, fourcc2 = peek_header(f)
        if fourcc2 == fourcc:
            return size
        f.seek(f.tell() + size)
        
def skip_atom(f):
    size, _ = peek_header(f)
    f.seek(f.tell() + size)


def parse_atom(f, until=None):
    pos = f.tell()
    if until and pos >= until:
        return False

    size, fourcc = peek_header(f)
    #print(pos, size, fourcc)
    
    if fourcc in types:
        head_size, has_children = types[fourcc]
        
        head = b''
        if head_size:
            head = read_data(f, head_size)
        else:
            f.seek(pos + ATOM_HEAD_SIZE)

        atom = Atom(fourcc, head)

        if has_children:
            while True:
                child = parse_atom(f, pos + size)
                if child:
                    atom.children.append(child)
                else:
                    break
    else:
        data = read_data(f, size - ATOM_HEAD_SIZE)
        atom = Atom(fourcc, data)
    
    f.seek(pos + size)
    return atom


def parse_file(f):
    atoms = []
    try:
        while True:
            atoms.append( parse_atom(f) )
    except:pass
    return atoms




