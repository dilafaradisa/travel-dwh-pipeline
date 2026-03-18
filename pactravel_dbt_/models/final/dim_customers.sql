with stg_dim_customers as (
    select
        customer_id as nk_customer_id,
        customer_first_name,
        customer_family_name,
        customer_gender,
        customer_country
    from {{ ref("stg_pactravel__customers") }}
),

final_dim_customers as (
    select
        {{ dbt_utils.generate_surrogate_key( ["nk_customer_id"] ) }} as sk_customer_id,
        *,
        {{ dbt_date.now() }} as created_at,
        {{ dbt_date.now() }} as updated_at
    from stg_dim_customers
)

select * from final_dim_customers