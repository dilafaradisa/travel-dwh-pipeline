select * 
from {{ source("pactravel-dwh", "aircrafts") }}