with dim_date as (
    select * from {{ ref("dim_date") }}
),
dim_customers as (
    select * from {{ ref("dim_customers") }}
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
fact_hotel_booking as (
    select
        {{ dbt_utils.generate_surrogate_key(["shb.trip_id", "shb.customer_id", "shb.hotel_id"]) }} as sk_hotel_booking_id,
        shb.trip_id,
        dc.sk_customer_id,
        dh.sk_hotel_id,
        dd1.date_actual as checkin_date_id,
        dd2.date_actual as checkout_date_id,
        shb.price as room_price,
        (dd2.date_actual - dd1.date_actual) as num_nights,
        shb.price * (dd2.date_actual - dd1.date_actual) as total_price,
        shb.breakfast_included,
        {{ dbt_date.now() }} as created_at,
        {{ dbt_date.now() }} as updated_at

    from stg_hotel_bookings shb
    left join dim_customers dc
        on dc.nk_customer_id = shb.customer_id
    left join dim_hotels dh
        on dh.nk_hotel_id = shb.hotel_id
    left join dim_date dd1
        on dd1.date_actual = shb.check_in_date
    left join dim_date dd2
        on dd2.date_actual = shb.check_out_date
)
select * from fact_hotel_booking