import dataclasses

import bitstruct as bs

from sateda.io.rtcm import RTCM


@RTCM.register_subclass(1020)
@dataclasses.dataclass
class Rtcm1020:
    message_number: int = 1020
    glonass_satellite_id: int = 0
    glonass_frequency_channel_number: int = 0
    glonass_almanac_health: int = 0
    glonass_almanac_indicator: int = 0
    glonass_p1: int = 0
    glonass_tk: int = 0
    glonass_mbs: int = 0

    glonass_p2: int = 0
    glonass_tb: int = 0
    glonass_xdot: int = 0
    glonass_x: int = 0
    glonass_xdotdot: int = 0
    glonass_ydot: int = 0
    glonass_y: int = 0
    glonass_ydotdot: int = 0
    glonass_zdot: int = 0
    glonass_z: int = 0
    glonass_zdotdot: int = 0
    glonass_p3: int = 0
    glonass_gamma_n: int = 0
    glonass_m_p: int = 0
    glonass_m_in: int = 0
    glonass_tauntaub: int = 0
    glonass_m_deltatn: int = 0
    glonass_em: int = 0
    glonass_mp4: int = 0

    glonass_mft: int = 0
    glonass_mnt: int = 0
    glonass_mm: int = 0
    glonass_additional_data: int = 0
    glonass_na: int = 0
    glonass_tauc: int = 0
    glonass_m_n4: int = 0
    glonass_m_tgps: int = 0
    glonass_m_in5: int = 0
    glonass_reserved: int = 0

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
