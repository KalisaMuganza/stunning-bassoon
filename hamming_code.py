from collections import namedtuple
integrity = namedtuple('status','master_parity_bit location double_digit outcome')

parity_bits = [1,2,4,8,16,32,64]
parity_mask = list()


def ecc_init_data():
    for i in parity_bits:
        parity_mask.append((2**(i-1)-1))

def ecc_compute_parity_master(data64_72):
    count =0
    for i in range(72):
        count += (data64_72>>i)&0x1
    return count&1

def ecc_compute_parity(data64_72,parity):
    count=0
    for i in range(parity-1,71,parity*2):
        for j in range(parity):
            if(i+j>70):
                break
            count+= (data64_72>>(i+j))&0x1
    return count&1
    

def ecc_encode72_64(data64):
    ecc_init_data()
    encoded_data64_72 = data64<<2
    for i in range(2,len(parity_bits)):
        temp = encoded_data64_72 & parity_mask[i]
        encoded_data64_72= (encoded_data64_72>>parity_bits[i]-1)<<parity_bits[i]
        encoded_data64_72=encoded_data64_72|temp
    
    for i in parity_bits:
        parity = ecc_compute_parity(encoded_data64_72,i)
        encoded_data64_72 |= parity<<(i-1)
    parity = ecc_compute_parity_master(encoded_data64_72)
    encoded_data64_72 |=parity<<71
    
    return encoded_data64_72
 
def ecc_decode72_64(encoded_data64_72):
    ecc_init_data()
    decode_location =0
    decode_double_digit =0
    decode_outcome =0

    for i in range(len (parity_bits)):
        decode_parity = ecc_compute_parity(encoded_data64_72,parity_bits[i])
        decode_location |= decode_parity<<i
      
    decode_master_parity_bit = ecc_compute_parity_master(encoded_data64_72)

    if decode_master_parity_bit ==0 and decode_location ==0:
        decode_outcome =1

    if decode_master_parity_bit ==0 and decode_location != 0:
        decode_double_digit =1
    
    status = integrity(decode_master_parity_bit,decode_location,decode_double_digit,decode_outcome)

    return status