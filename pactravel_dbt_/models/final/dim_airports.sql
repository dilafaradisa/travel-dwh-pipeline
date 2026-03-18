with stg_dim_airports as (
    select
        airport_id as nk_airport_id,
        airport_name,
        city,
        latitude,
        longitude
    from {{ ref("stg_pactravel__airports") }}
),

final_dim_airports as (
    select
        {{ dbt_utils.generate_surrogate_key( ["nk_airport_id"] ) }} as sk_airport_id,
        *,
        {{ dbt_date.now() }} as created_at,
        {{ dbt_date.now() }} as updated_at
    from stg_dim_airports
)

select * from final_dim_airports