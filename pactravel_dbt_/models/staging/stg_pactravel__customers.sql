select * 
from {{ source("pactravel-dwh", "customers") }}