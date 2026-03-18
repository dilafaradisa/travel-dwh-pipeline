with dim_date as (
    select * from {{ ref("dim_date") }}
),
dim_hotels as (
    select * from {{ ref("dim_hotel") }}
),
stg_hotel_bookings as (
    select
        trip_id,
        customer_id,
        hotel_id,
        check_in_date,
        check_out_date,
        price,
        breakfast_included
    from {{ ref("stg_pactravel__hotel_bookings") }}
),
fact_daily_hotel_summary as (
    select
        dd1.date_actual as booking_date,
        dh.nk_hotel_id,
        count(shb.trip_id) as total_bookings,
        avg(shb.price) as avg_room_price,
        sum(shb.price * (dd2.date_actual - dd1.date_actual)) as total_revenue,
        count(distinct shb.customer_id) as unique_customers,
        sum(case when shb.breakfast_included then 1 else 0 end) as bookings_with_breakfast,
        {{ dbt_date.now() }} as created_at,
        {{ dbt_date.now() }} as updated_at

    from stg_hotel_bookings shb
    
    left join dim_hotels dh
        on dh.nk_hotel_id = shb.hotel_id
    left join dim_date dd1
        on dd1.date_actual = shb.check_in_date
    left join dim_date dd2
        on dd2.date_actual = shb.check_out_date

    group by
        dd1.date_actual,
        dh.nk_hotel_id
)
select * from fact_daily_hotel_summary