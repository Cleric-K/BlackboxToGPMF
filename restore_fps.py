import mp4
import sys, struct, shutil, os

outname = os.path.basename(sys.argv[1])
name, ext = os.path.splitext(outname)
outname = name + '_org_fps' + ext
print(outname)
f = open(sys.argv[1], 'rb')
mp4.find_atom(f, b'moov')
moov_offset = f.tell()
moov = mp4.parse_atom(f)

for trak in moov.find(b'trak'):
    if trak.find(b'vmhd'):
        video_trak = trak
        break
else:
    sys.exit(1)

#stsz = video_trak.find(b'stsz')[0]
stts = video_trak.find(b'stts')[0]
mdhd = video_trak.find(b'mdhd')[0]

#num_samples = struct.unpack('>I', stsz.data[8:8+4])[0]
#stts.data[4:] = struct.pack('>III', 1, num_samples, 1001)
stts_entries = struct.unpack('>I', stts.data[4:4+4])[0]
num_samples = 0
for i in range(stts_entries):
    offset = 8 + i*8
    num_samples += struct.unpack('>I', stts.data[offset:offset+4])[0]
    stts.data[offset+4:offset+8] = struct.pack('>I', 1000)
    print(struct.unpack('>I', stts.data[offset:offset+4])[0], struct.unpack('>I', stts.data[offset+4:offset+8])[0])

print(struct.unpack('>II', mdhd.data[12:12+8]))
mdhd.data[12:12+8] = struct.pack('>II', 60000, num_samples*1000)
f.close()
#sys.exit()
#os.unlink(outname)
shutil.copyfile(sys.argv[1], outname)
fout = open(outname, 'r+b')
fout.seek(moov_offset)
fout.write(moov.flatten())
