from PIL import Image

QR_SIZE = 21
QUIET_ZONE = 0
GRID_SIZE = QR_SIZE + QUIET_ZONE
RESERVED = [[-1 for _ in range(QR_SIZE)] for _ in range(QR_SIZE)]

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
                RESERVED[row][col] = 1

                qr.putpixel((QR_SIZE-7+col, row), (0, 0, 0))
                RESERVED[row][QR_SIZE-7+col] = 1

                qr.putpixel((col, QR_SIZE-7+row), (0, 0, 0))
                RESERVED[QR_SIZE-7+row][col] = 1


def draw_tp(qr):
    for col in range(8, GRID_SIZE-8, 2):
        qr.putpixel((col, 6), (0, 0, 0))
        RESERVED[6][col] = 1

    for row in range(8, GRID_SIZE-8, 2):
        qr.putpixel((6, row), (0, 0, 0))
        RESERVED[row][6] = 1

def zig_zag_deez_nuts(data_format):
    bits = list(data_format)

    wasLeft = False
    row = GRID_SIZE-1;
    col = GRID_SIZE-1;
    
    for i in range(len(bits)):
        if bits[i] == '1':
            qr.putpixel((col, row), (0, 0, 0))

        if wasLeft:
            col+=1
            row-=1

        else:
            col-=1
        
        wasLeft = not wasLeft
        

if __name__ == "__main__":
    qr = Image.new(mode="RGB", size=(GRID_SIZE, GRID_SIZE), color="white")
    draw_pp(qr)
    draw_tp(qr)
    zig_zag_deez_nuts("0100")

    qr.show()

