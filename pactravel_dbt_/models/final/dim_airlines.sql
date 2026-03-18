with stg_dim_airlines as (
    select
        airline_id as nk_airline_id,
        airline_name,
        country,
        airline_iata,
        airline_icao,
        alias
    from {{ ref("stg_pactravel__airlines") }}
),

final_dim_airlines as (
    select
        {{ dbt_utils.generate_surrogate_key( ["nk_airline_id"] ) }} as sk_airline_id,
        *,
        {{ dbt_date.now() }} as created_at,
        {{ dbt_date.now() }} as updated_at
    from stg_dim_airlines
)

select * from final_dim_airlines