from Models.parkinglot import ParkingLot

class BuildingBuilder:

    def __init__(self, normal_parking_space_amount:int, special_parking_space_amount:int = 0):
        self.parking_lot = ParkingLot(normal_parking_space_amount, special_parking_space_amount)

    @property
    def general_amount_of_parking_spaces(self):
        return self.parking_lot.parking_space_amount

    @property
    def amount_of_normal_parking_spaces(self):
        return self.parking_lot.normal_parking_space_amount

    @property
    def amount_of_special_parking_spaces(self):
        return self.parking_lot.special_parking_space_amount
    