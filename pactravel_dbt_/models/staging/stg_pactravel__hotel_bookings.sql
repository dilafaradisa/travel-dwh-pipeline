select * 
from {{ source("pactravel-dwh", "hotel_bookings") }}