import dataclasses
import bitstruct as bs

from sateda.io.rtcm import RTCM


@RTCM.register_subclass(1006)
@dataclasses.dataclass
class Rtcm1006:
    message_number: int = 1006
    reference_station_id: int = 0
    itrf_year: int = 0
    gps_indicator: bool = False
    glonass_indicator: bool = False
    galileo_indicator: bool = False
    reference_station_indicator: bool = False
    ecef_x: int = 0
    oscillator_indicator: bool = False
    reserved: int = 0
    ecef_y: int = 0
    quarter_cycle_indicator: bool = False
    ecef_z: int = 0
    antenna_height: int = 0

    def __str__(self):
        return str(dataclasses.asdict(self))

    @classmethod
    def decode(cls, binary_message):
        #first byte
        assert binary_message[0] == 0xD3
        # 6 bits of '0' than 2 bits + next 8 of data length
        data_length = ((binary_message[1] & 0b00000011) << 8) | binary_message[2]
        print(data_length)
        #real message starts now.
        message = binary_message[3:3+data_length]
        extracted = bs.unpack_from('u12u12u6u1u1u1u1s38u1u1s38u2s38u16', message)

        return cls(message_number=extracted[0],
                   reference_station_id=extracted[1],
                   itrf_year=extracted[2],
                   gps_indicator=extracted[3],
                   glonass_indicator=extracted[4],
                   galileo_indicator=extracted[5],
                   reference_station_indicator=extracted[6],
                   ecef_x=extracted[7],
                   oscillator_indicator=extracted[8],
                   reserved=extracted[9],
                   ecef_y=extracted[10],
                   quarter_cycle_indicator=extracted[11],
                   ecef_z=extracted[12],
                   antenna_height=extracted[13])

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
