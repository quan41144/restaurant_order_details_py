create type table_status as enum ('empty', 'occupied');
create type order_status as enum ('pending', 'cooking', 'done', 'cancelled');
create type payment_method as enum ('cash', 'card', 'qr');
create type payment_status as enum ('unpaid', 'paid', 'failed');
-- TABLE
create table order_tables (
	id serial primary key,
	name varchar(50),
	status table_status default 'empty'
);
-- MENU
create table menu_items (
	id serial primary key,
	name varchar(100) not null,
	price numeric(10, 2) not null,
	category varchar(50)
);
-- Cart
create table carts (
	id serial primary key,
	table_id int unique,
	created_at timestamp default current_timestamp,
	foreign key (table_id) references order_tables(id) on delete cascade
);
-- Cart item
create table cart_items (
	id serial primary key,
	cart_id int,
	menu_item_id int,
	quantity int check (quantity > 0),
	foreign key (cart_id) references carts(id) on delete cascade,
	foreign key (menu_item_id) references menu_items(id)
);
-- Order
create table orders (
	id serial primary key,
	table_id int,
	status order_status default 'pending',
	created_at timestamp default current_timestamp,
	foreign key (table_id) references order_tables(id)
);
-- Order Item
create table order_items (
	id serial primary key,
	order_id int,
	menu_item_id int,
	quantity int check (quantity > 0),
	foreign key (order_id) references orders(id) on delete cascade,
	foreign key (menu_item_id) references menu_items(id)
);
-- payment
create table payments (
	id serial primary key,
	order_id int unique,
	total_amount numeric(10, 2),
	method payment_method,
	status payment_status default 'unpaid',
	created_at timestamp default current_timestamp,
	foreign key (order_id) references orders(id)
);
ALTER TABLE menu_items
ADD COLUMN image TEXT;
INSERT INTO menu_items (name, price, image, category) VALUES
('Phở bò', 50000, 'app/assets/images/pho_bo.jpg', 'Món nước'),
('Bún chả', 45000, 'app/assets/images/bun_cha.jpg', 'Món nước'),
('Cơm tấm sườn', 55000, 'app/assets/images/com_tam.jpg', 'Cơm'),
('Gà rán', 60000, 'app/assets/images/ga_ran.jpg', 'Món chiên'),
('Trà sữa', 30000, 'app/assets/images/tra_sua.jpg', 'Đồ uống'),
('Cà phê đen', 25000, 'app/assets/images/cf_den.jpg', 'Đồ uống'),
('Cà phê sữa', 30000, 'app/assets/images/cf_sua.jpg', 'Đồ uống'),
('Bánh mì thịt', 20000, 'app/assets/images/banh_mi.jpg', 'Ăn nhanh'),
('Mì xào bò', 50000, 'app/assets/images/mi_xao.jpg', 'Món xào'),
('Lẩu thái', 120000, 'app/assets/images/lau_thai.jpg', 'Lẩu');
INSERT INTO order_tables (name, status) VALUES
('Bàn 1', 'empty'),
('Bàn 2', 'empty'),
('Bàn 3', 'empty'),
('Bàn 4', 'empty');
select * from menu_items;
select * from payments;