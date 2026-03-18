with dim_date as (
    select * from {{ ref("dim_date") }}
),
dim_airlines as (
    select * from {{ ref("dim_airlines") }}
),
stg_flight_bookings as (
    select
        trip_id,
        customer_id,
        airline_id,
        departure_date,
        price
    from {{ ref("stg_pactravel__flight_bookings") }}
),
fact_daily_flight_bookings as (
    select
        dd.date_actual as booking_date,
        dal.sk_airline_id as airline_id,
        count(sfb.trip_id) as total_bookings,
        sum(sfb.price) as total_revenue,
        avg(sfb.price) as avg_ticket_price,
        count(distinct sfb.customer_id) as unique_customers,
        {{ dbt_date.now() }} as created_at,
        {{ dbt_date.now() }} as updated_at

    from stg_flight_bookings sfb
    left join dim_airlines dal
        on dal.nk_airline_id = sfb.airline_id
    left join dim_date dd
        on dd.date_actual = sfb.departure_date
    group by
        dd.date_actual,
        dal.sk_airline_id
)
select * from fact_daily_flight_bookings
