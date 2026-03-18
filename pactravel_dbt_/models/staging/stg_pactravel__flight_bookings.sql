select * 
from {{ source("pactravel-dwh", "flight_bookings") }}