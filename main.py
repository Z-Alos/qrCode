from reedsolo import RSCodec
from PIL import Image

QR_SIZE = 21
QUIET_ZONE = 0
GRID_SIZE = QR_SIZE + QUIET_ZONE
RESERVED = [[False for _ in range(QR_SIZE)] for _ in range(QR_SIZE)]
MODULES = [[0 for _ in range(QR_SIZE)] for _ in range(QR_SIZE)]

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

                MODULES[row][col] = 1
                MODULES[row][QR_SIZE-7+col] = 1
                MODULES[QR_SIZE-7+row][col] = 1

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

def calculate_format_info(data_bits_5bit):
    generator = 0b10100110111  # 0x537
    data_bits_5bit &= 0b11111  # Force only 5 bits
    data = data_bits_5bit << 10  # Append 10 zero bits
    
    # Do mod-2 division (XOR when MSB aligns)
    for i in range(14, 9, -1):
        if data & (1 << i):
            data ^= generator << (i - 10)
    
    bch_code = data 
    full_format_info = (data_bits_5bit << 10) | bch_code
    masked = full_format_info ^ 0b101010000010010  # Format mask

    return f"{masked:015b}"  


def draw_fip(qr, mask_type):
    #first 5 bits
    ec_level = "01"

    MASK_TYPES = {
        0: "000",  
        1: "001", 
        2: "010",
        3: "011",
        4: "100", 
        5: "101",
        6: "110",
        7: "111"
    }

    first_5_bit= ec_level+MASK_TYPES[mask_type]

    #BCH
    bch = calculate_format_info(int(first_5_bit, 2))
    print(bch)
    bits = list(bch) 
    bit_idx = 0

    #First Copy (Top-Left Position Pattern)
    #First 7 bits goes left to right 
    #Last 8 bits goes vertically top to bottom 

    #Horizontal
    for col in range(8):
        if col == 6:
            continue

        if bits[bit_idx] == "1":
            qr.putpixel((col, 8), (51, 137, 55))
            MODULES[8][col] = 1

        RESERVED[8][col] = True
        bit_idx+=1

    #Vertical
    for row in range(9):
        if row == 6:
            continue

        if bits[bit_idx] == "1":
            qr.putpixel((8, row), (51, 137, 55))
            MODULES[row][8] = 1

        RESERVED[row][8] = True
        bit_idx+=1
        
    
    #Mirror Copy
    bit_idx = 0

    for row in range(7):
        if bits[bit_idx] == "1":
            qr.putpixel((8, QR_SIZE-1-row), (51, 137, 55))
            MODULES[QR_SIZE-1-row][8] = 1

        RESERVED[QR_SIZE-1-row][8] = True
        bit_idx+=1

    for col in range(8):
        if bits[bit_idx] == "1":
            qr.putpixel((QR_SIZE-1-col, 8), (151, 137, 55))
            MODULES[8][QR_SIZE-1-col] = 1

        RESERVED[8][QR_SIZE-1-col] = True
        bit_idx+=1

    #Draw The Stagnant 
    qr.putpixel((8, QR_SIZE-8), (0, 0, 0))
    RESERVED[QR_SIZE-8][8] = True   
    MODULES[QR_SIZE-8][8] = 1   
    

def draw_tp(qr):
    for col in range(8, GRID_SIZE-8, 1):
        if col%2 == 0:
            qr.putpixel((col, 6), (0, 0, 0))
            MODULES[6][col] = 1

        RESERVED[6][col] = True

    for row in range(8, GRID_SIZE-8, 1):
        if row%2 == 0:
            qr.putpixel((6, row), (0, 0, 0))
            MODULES[row][6] = 1
            
        RESERVED[row][6] = True

def encode_data(data):
    mode_indicator = "0100"
    char_count = f"{len(data):08b}"
    data_bits = ''.join(f"{byte:08b}" for byte in data)

    bit_stream = mode_indicator + char_count + data_bits

    # Add upto 4 terminator bits(0)
    max_bits = 152  
    bit_stream += '0' * min(4, max_bits - len(bit_stream))

    # Pad to byte alignment
    while len(bit_stream) % 8 != 0:
        bit_stream += '0'

    # convert to byte array
    data_bytes = bytearray(int(bit_stream[i:i+8], 2) for i in range(0, len(bit_stream), 8))

    # pad to 19 bytes (Version 1-L)
    pad_bytes = [0xEC, 0x11]
    while len(data_bytes) < 19:
        data_bytes.append(pad_bytes[len(data_bytes) % 2])

    rsc = RSCodec(7)
    full = rsc.encode(data_bytes)
    return ''.join(f'{byte:08b}' for byte in full)


def zig_zag_deez_nuts(bits, data):
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
                        MODULES[y][x] = 1
                    bit_idx += 1        

        col-=2

def apply_mask(mask_id):
    size = len(MODULES)

    def mask_condition(r, c):
        if mask_id == 0:
            return (r + c) % 2 == 0
        elif mask_id == 1:
            return r % 2 == 0
        elif mask_id == 2:
            return c % 3 == 0
        elif mask_id == 3:
            return (r + c) % 3 == 0
        elif mask_id == 4:
            return (r // 2 + c // 3) % 2 == 0
        elif mask_id == 5:
            return (r * c) % 2 + (r * c) % 3 == 0
        elif mask_id == 6:
            return ((r * c) % 2 + (r * c) % 3) % 2 == 0
        elif mask_id == 7:
            return ((r + c) % 2 + (r * c) % 3) % 2 == 0

    for r in range(size):
        for c in range(size):
            if not RESERVED[r][c] and mask_condition(r, c):
                MODULES[r][c] ^= 1


if __name__ == "__main__":
    data = b"www.youtube.com"
    mask_type = 3

    qr = Image.new(mode="RGB", size=(GRID_SIZE, GRID_SIZE), color="white")
    draw_pp(qr)
    draw_fip(qr, mask_type=mask_type)
    draw_tp(qr)
    bits = encode_data(data)
    zig_zag_deez_nuts(bits, data)
    apply_mask(mask_type)


    #qr code with Matrix
    for row in range(QR_SIZE):
        for col in range(QR_SIZE):
            if MODULES[row][col] == 1:
                qr.putpixel((col, row), (0, 0, 0))
            else:
                qr.putpixel((col, row), (255, 255, 255))

    qr.show()



