import dataclasses

import bitstruct as bs


@dataclasses.dataclass
class Rtcm1033:
    message_number: int = 1033
    reference_station_id: int = 0
    antenna_descriptor_counter: int = 0

    def __str__(self):
        return str(dataclasses.asdict(self))

    @classmethod
    def decode(cls, binary_message):
        # first byte
        assert binary_message[0] == 0xD3
        # 6 bits of '0' than 2 bits + next 8 of data length
        data_length = ((binary_message[1] & 0b00000011) << 8) | binary_message[2]
        print(data_length)
        # real message starts now.
        message = binary_message[3:3 + data_length]
        extracted = bs.unpack_from('u12u6u5u1u1u2u12u1u1u7s24s27s5s24s27s5s24s27s5u1s11u2u1s22s5u5u1u4u11u2u1u11s32u5u22u1u7', message)

        return cls(*extracted)

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
