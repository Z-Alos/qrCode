from reedsolo import RSCodec
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

    #position pattern seperator (white zone)
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

# learn about BCH (this func is llm generated)
def calculate_format_info(data_bits_5bit):
    generator = 0b10100110111  # 0x537
    data_bits_5bit &= 0b11111  # Force only 5 bits
    data = data_bits_5bit << 10  # Append 10 zero bits
    
    # Do mod-2 division (XOR when MSB aligns)
    for i in range(14, 9, -1):
        if data & (1 << i):
            data ^= generator << (i - 10)
    
    bch_code = data  # Now contains the 10-bit BCH
    full_format_info = (data_bits_5bit << 10) | bch_code
    masked = full_format_info ^ 0b101010000010010  # Format mask

    return f"{masked:015b}"  # Final 15-bit string

# ECC: Q = 0b11, Mask pattern: 7 = 0b111 → Combined: 0b11111 = 31


def draw_fip(qr):
    #first 5 bits
    ec_level = "11"
    mask_type = "111"
    first_5_bit= ec_level+mask_type

    #BCH
    bch = calculate_format_info(int(first_5_bit))
    print(bch)
    bits = list(bch) 
    bit_idx = 0

    #First Copy (Top-Left Position Pattern)
    #First 7 bits goes down
    #Last 8 bits goes left to right

    #Vertical
    for row in range(8):
        if row == 6:
            continue

        if bits[bit_idx] == "1":
            qr.putpixel((8, row), (51, 137, 55))

        RESERVED[row][8] = True
        bit_idx+=1

    #Horizontal
    for col in range(9):
        if col == 6:
            continue

        if bits[bit_idx] == "1":
            qr.putpixel((col, 8), (51, 137, 55))

        RESERVED[8][col] = True
        bit_idx+=1
        
    
    #Mirror Copy
    bit_idx = 0

    for row in range(7):
        if bits[bit_idx] == "1":
            qr.putpixel((8, QR_SIZE-1-row), (51, 137, 55))

        RESERVED[QR_SIZE-1-row][8] = True
        bit_idx+=1

    for col in range(8):
        if bits[bit_idx] == "1":
            qr.putpixel((QR_SIZE-1-col, 8), (151, 137, 55))

        RESERVED[8][QR_SIZE-1-col] = True
        bit_idx+=1

    #Draw The Stagnant 
    qr.putpixel((8, QR_SIZE-8), (0, 0, 0))
    RESERVED[QR_SIZE-8][8] = True   
    

def draw_tp(qr):
    for col in range(8, GRID_SIZE-8, 1):
        if col%2 == 0:
            qr.putpixel((col, 6), (0, 0, 0))
        RESERVED[6][col] = True

    for row in range(8, GRID_SIZE-8, 1):
        if row%2 == 0:
            qr.putpixel((6, row), (0, 0, 0))
        RESERVED[row][6] = True

def encode_data(data):
    data_padded = data.ljust(19, b'\x00')  # OR using pad bytes like 0xEC and 0x11 alternating

    rsc = RSCodec(7)
    ecc = rsc.encode(data_padded)[-7:]  # Just get the last 7 ECC bytes

    codewords = data_padded + ecc     
    # codewords = data_padded 
    bits = ''.join(f'{byte:08b}' for byte in codewords)

    return bits 


def zig_zag_deez_nuts(bits):
    bits = list(bits)
    size = len(RESERVED)
    col = QR_SIZE-1
    bit_idx = 0 

    while col > 0:
        if col == 6: #i.e 7th col
            col-=1

        for row in (range(size-1, -1, -1) if (col // 2) % 2 == 0 else range(size)):
            for offset in [0, -1]:
                x = col + offset 
                y = row
                if 0 <= x < size and 0 <= y < size and not RESERVED[y][x]:
                    if bit_idx < len(bits) and bits[bit_idx] == "1":
                        qr.putpixel((x, y), (255, 0, 0))
                    bit_idx += 1        

        col-=2

if __name__ == "__main__":
    data = b"Hello, World fucke"
    qr = Image.new(mode="RGB", size=(GRID_SIZE, GRID_SIZE), color="white")
    draw_pp(qr)
    draw_fip(qr)
    draw_tp(qr)
    bits = encode_data(data)
    zig_zag_deez_nuts(bits)

    qr.show()

