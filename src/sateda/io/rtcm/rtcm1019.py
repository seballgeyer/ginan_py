import dataclasses

import bitstruct as bs

from  sateda.io.rtcm import RTCM


@RTCM.register_subclass(1019)
@dataclasses.dataclass
class Rtcm1019:
    message_number: int = 1019
    gps_satellite_id: int = 0
    gps_week_number: int = 0
    gps_sv_accuracy: int = 0
    gps_code_on_l2: int = 0
    gps_idot: int = 0
    gps_iode: int = 0
    gps_toc: int = 0
    gps_af2: int = 0
    gps_af1: int = 0
    gps_af0: int = 0
    gps_iodc: int = 0
    gps_crs: int = 0
    gps_deltan: int = 0
    gps_m0: int = 0
    gps_cuc: int = 0
    gps_eccentricity: int = 0
    gps_cus: int = 0
    gps_sqrt_a: int = 0
    gps_toe: int = 0
    gps_cic: int = 0
    gps_omega0: int = 0
    gps_cis: int = 0
    gps_i0: int = 0
    gps_crc: int = 0
    gps_omega: int = 0
    gps_omega_dot: int = 0
    gps_tgd: int = 0
    gps_health: int = 0
    gps_l2_p_data_flag: bool = 0
    gps_fit_interval: bool = 0

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
        extracted = bs.unpack_from('u12u6u10u4u2s14u8u16s8s16s22u10s16s16s32s16u32s16u32u16s16s32s16s32s16s32s24s8u6u1u1', message)

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
