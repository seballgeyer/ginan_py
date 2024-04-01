import dataclasses

import bitstruct as bs
from typing import List

from sateda.io.rtcm import RTCM


@RTCM.register_subclass(1013)
@dataclasses.dataclass
class Rtcm1013:
    message_number: int = 1013
    reference_station_id: int = 0
    mjd: int = 0
    seconds_of_day: int = 0
    number_of_messages: int = 0
    leap_seconds: int = 0
    data: List[dict] = dataclasses.field(default_factory=list)

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
        extracted = bs.unpack_from('u12u12u16u17u5u8', message)
        offset = 12 + 12 + 16 + 17 + 5 + 8
        infos = []
        for i in range(extracted[4]):
            data = bs.unpack_from('u12u1u16', message, offset=offset)
            offset += 12 + 1 + 16
            infos.append({"id": data[0],
                          "sync": data[1],
                          "transmission_interval": data[2]}
                         )

        return cls(*extracted, data=infos)

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
