create type Side as enum ('buy', 'sell');
create type Status as enum ('unfilled', 'filled', 'cancelled');

create table InstrumentType (
	id serial not null,
	description varchar(255) not null,
	primary key (id)
);

create table Account (
	id varchar(30) not null,
	name varchar(255) not null,
	balance int not null,
	primary key (id)
);

create table Instrument (
	id serial not null,
	type_id int not null references InstrumentType(id),
	display_order int not null,
	week_number int,
	is_active boolean not null,
	did_occur boolean,
	primary key (id)
);

create table Position (
	account_id varchar(30) not null references Account(id),
	instrument_id int not null references Instrument(id),
	num_positions int not null,
	primary key (account_id, instrument_id)
);

create table Transaction (
	id serial not null,
	transaction_time timestamp not null,
	buyer_id varchar(30) not null references Account(id),
	seller_id varchar(30) not null references Account(id),
	maker_side Side not null,
	instrument_id int not null references Instrument(id),
	price int not null,
	primary key (id)
);

create table TradeOrder (
	id serial not null,
	order_time timestamp not null,
	account_id varchar(30) not null references Account(id),
	side Side not null,
	price int not null,
	instrument_id int not null references Instrument(id),
	status Status not null,
	processed_time timestamp,
	primary key (id)
);
