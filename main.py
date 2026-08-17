from Buildings.building import Building_builder

from Parking_Fields.big_parking_field import Big_parking_field


Building = Building_builder(Big_parking_field)


print(Building.size_of_parking_field)