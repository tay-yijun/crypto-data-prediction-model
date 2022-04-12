create table public.bitcoin_price (
 id SERIAL PRIMARY KEY,
 event_time timestamp not null,
 btc_usd_price double precision not null
);

