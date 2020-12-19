import sys

f = open(sys.argv[1], 'rb')

print('binary = new Uint8Array([')
while True:
    c = f.read(1)
    if not c:
        break
    print(ord(c), ',')
print('])')