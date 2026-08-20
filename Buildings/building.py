from Parking_Lots.parking_lot import Parking_lot

class Building_builder():

    def __init__(self, normal_parking_space_amount, special_parking_space_amount = 0):

        self.parking_lot = Parking_lot(normal_parking_space_amount, special_parking_space_amount)


    @property
    def general_amount_of_parking_spaces(self):

        return self.parking_lot.get_parking_space_amount()

    @property
    def amount_of_normal_parking_spaces(self):

        return self.parking_lot.get_normal_parking_space_amount()

    @property
    def amount_of_special_parking_spaces(self):
    
        return self.parking_lot.get_special_parking_space_amount()
    a = 1