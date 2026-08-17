from .abs_parking_field import Abs_Parking_Field

class Big_parking_field(Abs_Parking_Field):

    @property
    def num_of_park_slots(self):
        return 12

