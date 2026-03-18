select * 
from {{ source("pactravel-dwh", "airports") }}