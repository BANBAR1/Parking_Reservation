class ParkingLot:
    def __init__(self, normal_parking_space_amount, special_parking_space_amount):

        self._normal_parking_space_amount = normal_parking_space_amount
        self._special_parking_space_amount = special_parking_space_amount

    @property
    def parking_space_amount(self):
        return self._normal_parking_space_amount + self._special_parking_space_amount

    @property
    def normal_parking_space_amount(self):
        return self._normal_parking_space_amount

    @property
    def special_parking_space_amount(self):
        return self._special_parking_space_amount