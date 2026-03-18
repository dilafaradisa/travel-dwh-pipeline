with dim_date as (
    select * from {{ ref("dim_date") }}
),
dim_customers as (
    select * from {{ ref("dim_customers") }}
),
dim_aircrafts as (
    select * from {{ ref("dim_aircrafts") }}
),
dim_airlines as (
    select * from {{ ref("dim_airlines") }}
),
dim_airports as (
    select * from {{ ref("dim_airports") }}
),
stg_flight_bookings as (
    select * from {{ ref("stg_pactravel__flight_bookings") }}
),
fact_flight_booking as (
    select
        {{ dbt_utils.generate_surrogate_key( ["sfb.trip_id", "sfb.flight_number", "sfb.seat_number"]) }} as sk_flight_booking_id,
        sfb.trip_id,
        sfb.flight_number,
        sfb.seat_number,
        dc.sk_customer_id,
        dal.sk_airline_id,
        dac.sk_aircraft_id,
        dap1.airport_name as departure_airport,
        dap2.airport_name as arrival_airport,
        dd.date_actual as departure_date,
        sfb.departure_time,
        sfb.flight_duration,
        sfb.travel_class,
        sfb.price as ticket_price,
        {{ dbt_date.now() }} as created_at,
        {{ dbt_date.now() }} as updated_at

    from stg_flight_bookings sfb

    left join dim_customers dc
        on dc.nk_customer_id = sfb.customer_id
    left join dim_airlines dal
        on dal.nk_airline_id = sfb.airline_id
    left join dim_aircrafts dac
        on dac.nk_aircraft_id = sfb.aircraft_id
    left join dim_airports dap1
        on dap1.nk_airport_id = sfb.airport_src
    left join dim_airports dap2
        on dap2.nk_airport_id = sfb.airport_dst
    left join dim_date dd
        on dd.date_actual = sfb.departure_date
)
select * from fact_flight_booking