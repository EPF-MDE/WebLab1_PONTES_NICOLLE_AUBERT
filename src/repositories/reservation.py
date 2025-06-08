from src.models.reservation import Reservation
from src.repositories.base import BaseRepository
from src.api.schemas.reservation import ReservationCreate

class ReservationRepository(BaseRepository[Reservation,ReservationCreate,None]):
    pass