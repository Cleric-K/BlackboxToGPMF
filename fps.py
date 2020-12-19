import mp4
import struct

def get_fps(f):
    f.seek(0)
    mp4.find_atom(f, b'moov')
    moov = mp4.parse_atom(f)

    for trak in moov.find(b'trak'):
        if trak.find(b'vmhd'):
            video_trak = trak
            break
    else:
        raise Exception('FPS: No video track found')


    stts = video_trak.find(b'stts')[0]
    mdhd = video_trak.find(b'mdhd')[0]


    stts_entries = struct.unpack('>I', stts.data[4:4+4])[0]
    sum_samples = 0
    sum_delta = 0
    for i in range(stts_entries):
        offset = 8 + i*8
        num_samples = struct.unpack('>I', stts.data[offset:offset+4])[0]
        sum_samples += num_samples
        sum_delta += num_samples * struct.unpack('>I', stts.data[offset+4:offset+8])[0]

    denom = round(sum_delta / sum_samples)
    numer = struct.unpack('>I', mdhd.data[12:12+4])[0]

    return numer, denom

def set_fps(f, numer, denom):
    f.seek(0)
    mp4.find_atom(f, b'moov')
    moov_offset = f.tell()
    moov = mp4.parse_atom(f)

    for trak in moov.find(b'trak'):
        if trak.find(b'vmhd'):
            video_trak = trak
            break
    else:
        raise Exception('FPS: No video track found')

    stts = video_trak.find(b'stts')[0]
    mdhd = video_trak.find(b'mdhd')[0]

    stts_entries = struct.unpack('>I', stts.data[4:4+4])[0]
    num_samples = 0
    for i in range(stts_entries):
        offset = 8 + i*8
        num_samples += struct.unpack('>I', stts.data[offset:offset+4])[0]
        stts.data[offset+4:offset+8] = struct.pack('>I', denom)

    mdhd.data[12:12+8] = struct.pack('>II', numer, num_samples*denom)

    f.seek(moov_offset)
    f.write(moov.flatten())

