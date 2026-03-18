select * 
from {{ source("pactravel-dwh", "hotel") }}