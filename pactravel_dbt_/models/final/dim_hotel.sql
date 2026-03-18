with stg_dim_hotel as (
    select
        hotel_id as nk_hotel_id,
        hotel_name,
        city,        
        country,
        hotel_score
    from {{ ref("stg_pactravel__hotel") }}
),

final_dim_hotel as (
    select
        {{ dbt_utils.generate_surrogate_key( ["nk_hotel_id"] ) }} as sk_hotel_id,
        *,
        {{ dbt_date.now() }} as created_at,
        {{ dbt_date.now() }} as updated_at
    from stg_dim_hotel
)

select * from final_dim_hotel