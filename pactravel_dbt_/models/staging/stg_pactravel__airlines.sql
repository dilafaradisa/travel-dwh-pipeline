select * 
from {{ source("pactravel-dwh", "airlines") }}