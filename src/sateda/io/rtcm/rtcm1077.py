import dataclasses

import bitstruct as bs

from sateda.io.rtcm import RTCM


@RTCM.register_subclass(1077)
@dataclasses.dataclass
class Rtcm1077:
    message_number: int = 1077
    reference_station_id: int = 0
    gnss_epoch: int = 0
    multiple_bits: int = 0
    iods: int = 0
    reserver: int = 0
    clock_steering_indicator: int = 0
    external_clock_indicator: int = 0
    gnss_divergence_free_smoothing_indicator: int = 0
    smooth_interval: int = 0
    satellite_mask: int = 0
    signal_mask: int = 0
    cell_mask: int = 0
    satellite_data: list = dataclasses.field(default_factory=list)
    signal_data: list = dataclasses.field(default_factory=list)

    def __str__(self):
        return str(dataclasses.asdict(self))

    def asdict(self):
        return dataclasses.asdict(self)
    @classmethod
    def decode(cls, binary_message):
        # first byte
        assert binary_message[0] == 0xD3
        # 6 bits of '0' than 2 bits + next 8 of data length
        data_length = ((binary_message[1] & 0b00000011) << 8) | binary_message[2]
        print(data_length)
        # real message starts now.
        message = binary_message[3:3 + data_length]
        extracted = bs.unpack_from('u12u12u30u1u3u7u2u2u1u3u64u32', message) # add cellmask
        #how many bit set to 1 in extract[5]
        nsat = bin(extracted[10]).count('1')
        nsig = bin(extracted[11]).count('1')
        cellmask = bs.unpack_from(f'u{nsat*nsig}', message, offset=169)
        #sat block:
        sat_data=[]
        print(extracted[10])
        for i in range(64):
            mask = 1 << i
            if extracted[10] & mask:
                print(f"Bit {i} is set to 1")
            else:
                print(f"Bit {i} is set to 0")
        print(bin(extracted[10]))
        binary_string = bin(extracted[10])[2:][::-1]
        # Get a list of the indices of the '1's
        indices = [i for i, bit in enumerate(binary_string) if bit == '1']
        print(indices)
        print(bin(extracted[11]))
        offset = 169+nsat*nsig
        for i in range(0, nsat):
            extracted_sat = bs.unpack_from('u8u4u10s14', message, offset=offset)
            sat_data.append({"int_milsec": extracted_sat[0],
                             "extended": extracted_sat[1],
                             "rough_range": extracted_sat[2]/1024,
                             "rough_phase": extracted_sat[3]
                             }
                            )
            offset += 36
        signal=[]
        for i in range(0, nsig):
            extracted_sig = bs.unpack_from('s20s24s10u1u10u15', message, offset=offset)
            signal.append({"fine_pseudo": extracted_sig[0],
                           "fine_range": extracted_sig[1],
                           "fine_range_lock": extracted_sig[2],
                           "half_amb": extracted_sig[3],
                           "cnr": extracted_sig[4],
                           "phaseRangeRate": extracted_sig[5]
                           }
                          )
            offset += 80

        return cls(*extracted, cell_mask=cellmask, satellite_data=sat_data, signal_data=signal)

    def encode(self):
        binary_message = b''

        # Encode the fields into the binary message
        binary_message += (self.message_number << 4).to_bytes(2, byteorder='big', signed=False)
        binary_message += (self.reference_station_id << 4).to_bytes(2, byteorder='big', signed=False)
        binary_message += (self.itrf_year << 2).to_bytes(1, byteorder='big')
        binary_message += self.gps_indicator.to_bytes(1, byteorder='big')
        binary_message += self.glonass_indicator.to_bytes(1, byteorder='big')
        binary_message += self.galileo_indicator.to_bytes(1, byteorder='big')
        binary_message += self.reference_station_indicator.to_bytes(1, byteorder='big')
        binary_message += (self.ecef_x << 6).to_bytes(5, byteorder='big')
        binary_message += self.oscillator_indicator.to_bytes(1, byteorder='big')
        binary_message += self.reserved.to_bytes(1, byteorder='big')
        binary_message += (self.ecef_y << 6).to_bytes(5, byteorder='big')
        binary_message += self.quarter_cycle_indicator.to_bytes(1, byteorder='big')
        binary_message += (self.ecef_z << 6).to_bytes(5, byteorder='big')
        binary_message += self.antenna_height.to_bytes(2, byteorder='big')

        return binary_message
