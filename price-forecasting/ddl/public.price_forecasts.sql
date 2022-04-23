create table public.price_forecasts (
 id SERIAL PRIMARY KEY,
 created_at timestamp default now(),
 forecast_future_time timestamp not null,
 forecast_btc_price double precision not null
);
