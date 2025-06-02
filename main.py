from enum import global_enum_repr
from PIL import Image

QR_SIZE = 21
QUIET_ZONE = 0
GRID_SIZE = QR_SIZE + QUIET_ZONE
RESERVED = [[False for _ in range(QR_SIZE)] for _ in range(QR_SIZE)]

def draw_pp(qr):
    pp_matrix = [
        [1,1,1,1,1,1,1],
        [1,0,0,0,0,0,1],
        [1,0,1,1,1,0,1],
        [1,0,1,1,1,0,1],
        [1,0,1,1,1,0,1],
        [1,0,0,0,0,0,1],
        [1,1,1,1,1,1,1]
    ]

    
    for row in range(7):
        for col in range(7):
            if pp_matrix[row][col] == 1:
                qr.putpixel((col, row), (0, 0, 0))
                qr.putpixel((QR_SIZE-7+col, row), (0, 0, 0))
                qr.putpixel((col, QR_SIZE-7+row), (0, 0, 0))

            RESERVED[row][col] = True
            RESERVED[row][QR_SIZE-7+col] = True
            RESERVED[QR_SIZE-7+row][col] = True

    #position pattern seperator
    #placing modules: top -> right -> bottom
    for row in range(8):
        qr.putpixel((7, row), (0, 0, 255))
        qr.putpixel((QR_SIZE-8, row), (0, 0, 255))
        qr.putpixel((7, QR_SIZE-8+row), (0, 0, 255))
        RESERVED[row][7] = True
        RESERVED[row][QR_SIZE-8] = True
        RESERVED[QR_SIZE-8+row][7] = True

    for col in range(8):
        qr.putpixel((col, 7), (0, 0, 255))
        qr.putpixel((QR_SIZE-8+col, 7), (0, 0, 255))
        qr.putpixel((col, QR_SIZE-8), (0, 0, 255))
        RESERVED[7][col] = True
        RESERVED[7][QR_SIZE-8+col] = True
        RESERVED[QR_SIZE-8][col] = True

def draw_tp(qr):
    for col in range(8, GRID_SIZE-8, 1):
        if col%2 == 0:
            qr.putpixel((col, 6), (0, 0, 0))
        RESERVED[6][col] = True

    for row in range(8, GRID_SIZE-8, 1):
        if row%2 == 0:
            qr.putpixel((6, row), (0, 0, 0))
        RESERVED[row][6] = True

def zig_zag_deez_nuts(data_format):
    bits = list(data_format)
    size = len(RESERVED)
    col = QR_SIZE-1
    bit_idx = 0 

    print(bits)

    while col > 0:
        if col == 6: #i.e 7th col
            col-=1

        for row in (range(size-1, -1, -1) if (col // 2) % 2 == 0 else range(size)):
            for offset in [0, -1]:
                x = col + offset 
                y = row
                if 0 <= x < size and 0 <= y < size and not RESERVED[y][x]:
                    if bit_idx < len(bits) and bits[bit_idx] == "1":
                        print("bitch")
                        qr.putpixel((x, y), (255, 0, 0))
                    bit_idx += 1        

        col-=2

if __name__ == "__main__":
    qr = Image.new(mode="RGB", size=(GRID_SIZE, GRID_SIZE), color="white")
    draw_pp(qr)
    draw_tp(qr)
    z_fill = "01011010"*17
    # zig_zag_deez_nuts("010000010001"+z_fill)

    qr.show()

