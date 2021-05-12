DROP DATABASE IF EXISTS blogly;

CREATE DATABASE blogly;

\c blogly

CREATE TABLE users
(
    id SERIAL PRIMARY KEY,
    first_name varchar(20) NOT NULL,
    last_name varchar(20) NOT NULL,
    image_url TEXT NOT NULL
);