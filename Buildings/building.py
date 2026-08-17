from Parking_Fields.abs_parking_field import Abs_Parking_Field

class Building_builder():

    def __init__(self, parking_field:Abs_Parking_Field):

        self.parking_field1 = parking_field()


    @property
    def size_of_parking_field(self):

        return self.parking_field1.num_of_park_slots
