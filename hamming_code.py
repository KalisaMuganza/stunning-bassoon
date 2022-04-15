
class Hamming64_72:
    
    from enum import Enum
    class ecc_t(Enum):
        ecc_ok=0 
        ecc_ok_master_parity=1 
        ecc_ok_single_bit=2
        ecc_ok_parity_bit=3 
        ecc_err_double_bit=4

    parity_bits = [1,2,4,8,16,32,64]
    parity_mask = list()
 
    @classmethod
    def ecc_init_data(cls):
        for i in cls.parity_bits:
            cls.parity_mask.append((2**(i-1)-1))
   
    @classmethod
    def ecc_compute_parity_master(cls,data64_72):
        count =0
        for i in range(71):
            count += (data64_72>>i)&0x1
        return count&1

    @classmethod
    def ecc_compute_parity(cls,data64_72,parity):
        count=0                                                  
        for i in range(parity-1,71,parity*2):
            for j in range(parity):
                if(i+j>70):
                    break
                count+= (data64_72>>(i+j))&0x1
        return count&1
    
    @classmethod
    def correct(cls,data64_72,position):
        """this method decodes the 72bit & corrects a single error
            it returns a 64 bit word"""

        if position:
            temp = 0X01<<(position-1)
            data64_72= data64_72^temp
        
        for mask in cls.parity_mask[:1:-1]:
            temp = data64_72 & mask
            data64_72 = ((data64_72 & (~mask))>>1)|temp
        data64_72= (data64_72>>2)&((2**64)-1)
      
        
        return data64_72

        
    @classmethod
    def ecc_encode72_64(cls,data64):
        cls.ecc_init_data()
        encoded_data = data64<<2
        for parity_bit,mask in zip(cls.parity_bits[2::],cls.parity_mask[2::]):
            temp = encoded_data & mask
            encoded_data= (encoded_data>>parity_bit-1)<<parity_bit
            #encoded_data64_72 = (encoded_data64_72 & ~parity_mask[i])<<1
            encoded_data=encoded_data|temp
        
        for i in cls.parity_bits:
            parity = cls.ecc_compute_parity(encoded_data,i)
            encoded_data |= parity<<(i-1)

        parity = cls.ecc_compute_parity_master(encoded_data)
        encoded_data |=parity<<71
        
        return encoded_data
    
    @classmethod
    def ecc_decode72_64(cls,encoded_data64_72):
        cls.ecc_init_data()
        cnt =0
        data64 = 0
        error_location =0
        decode_result = cls.ecc_t.ecc_err_double_bit

        
        master_parity_orig=(encoded_data64_72>>71)&0x1
        master_parity_new= cls.ecc_compute_parity_master(encoded_data64_72)
        
        
        for i in range(len (cls.parity_bits)):
            parity_value = cls.ecc_compute_parity(encoded_data64_72,cls.parity_bits[i])
            error_location |= parity_value<<i

            if parity_value:
                cnt +=1

            
        if master_parity_orig!= master_parity_new and cnt ==1:
            decode_result = cls.ecc_t.ecc_ok_parity_bit
            data64 = cls.correct(encoded_data64_72,0)
        
        if master_parity_new !=master_parity_orig and error_location ==0:
            decode_result = cls.ecc_t.ecc_ok_master_parity
            data64 = cls.correct(encoded_data64_72,0)

        if master_parity_new ==master_parity_orig and error_location ==0:
            decode_result = cls.ecc_t.ecc_ok
            data64 = cls.correct(encoded_data64_72,0)
            
        if cnt >1 and master_parity_new !=master_parity_orig and error_location !=0:
            decode_result = cls.ecc_t.ecc_ok_single_bit
            data64 = cls.correct(encoded_data64_72,error_location)

        return data64, decode_result