{% snapshot dim_hotel_snapshot %}

{{
    config(
        target_database="pactravel-dwh",
        target_schema="snapshots",     
        unique_key="sk_hotel_id",
        strategy="check",         
        check_cols=[
            "hotel_name", 
            "hotel_city", 
            "hotel_country", 
            "hotel_score"]
    )
}}

select
    *
from {{ ref("dim_hotel") }}

{% endsnapshot %}