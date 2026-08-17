import abc

class Abs_Parking_Field(abc.ABC):

    @property
    @abc.abstractmethod
    def num_of_park_slots(self):
        pass