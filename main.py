from Buildings.building import BuildingBuilder


Building = BuildingBuilder(4, 9)


print(Building.general_amount_of_parking_spaces)
print(Building.amount_of_normal_parking_spaces)
print(Building.amount_of_special_parking_spaces)