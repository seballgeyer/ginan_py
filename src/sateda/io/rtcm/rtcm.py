import dataclasses
@dataclasses.dataclass
class RTCM:
    subclass = {}

    @classmethod
    def register_subclass(cls, message_number):
        def decorator(subclass):
            cls.subclass[message_number] = subclass
            return subclass
        return decorator

    def __new__(cls, message_number, *args, **kwargs):
        if message_number in cls.subclass:
            return cls.subclass[message_number](*args, **kwargs)
        else:
            print(f"Unknown message number: {message_number}")
            return super().__new__(cls)

    def asdict(self):
        return dataclasses.asdict(self)

    def encode(self):
        pass

    def decode(self, binary_message):
        pass