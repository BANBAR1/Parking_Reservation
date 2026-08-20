class Parking_lot:

    def __init__(self, normal_parking_space_amount, special_parking_space_amount):

        parking_space_amount = normal_parking_space_amount+special_parking_space_amount

        self._parking_space_amount = parking_space_amount
        self._normal_parking_space_amount = normal_parking_space_amount
        self._special_parking_space_amount = special_parking_space_amount
        
    def get_parking_space_amount(self):
        return self._parking_space_amount
    
    def get_normal_parking_space_amount(self):
        return self._normal_parking_space_amount
    
    def get_special_parking_space_amount(self):
        return self._special_parking_space_amount