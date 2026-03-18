{% snapshot dim_customer_snapshot %}

{{
    config(
        target_database="pactravel-dwh",
        target_schema="snapshots",     
        unique_key="sk_customer_id",
        strategy="check",         
        check_cols=[
            "customer_first_name",
            "customer_last_name",
            "customer_gender",
            "customer_country"
            ]
    )
}}

select 
    *
from {{ ref("dim_customers") }}

{% endsnapshot %}