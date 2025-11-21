CREATE TABLE products (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    stock INT NOT NULL
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INT REFERENCES users(id),
    total_amount DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE order_items (
    id SERIAL PRIMARY KEY,
    order_id INT REFERENCES orders(id),
    product_id INT REFERENCES products(id),
    quantity INT NOT NULL,
    price_at_time DECIMAL(10, 2) NOT NULL
);

-- Insert sample data
INSERT INTO products (name, price, stock) VALUES
    ('Laptop Pro', 1299.99, 50),
    ('Wireless Mouse', 29.99, 200),
    ('Mechanical Keyboard', 149.99, 75),
    ('Monitor 4K', 399.99, 30),
    ('USB-C Hub', 49.99, 100);

INSERT INTO users (username, email) VALUES
    ('jdoe', 'john@example.com'),
    ('asmith', 'alice@example.com'),
    ('bwayne', 'bruce@wayne.com');

INSERT INTO orders (user_id, total_amount, status) VALUES
    (1, 1329.98, 'completed'),
    (2, 149.99, 'processing'),
    (3, 399.99, 'shipped');

INSERT INTO order_items (order_id, product_id, quantity, price_at_time) VALUES
    (1, 1, 1, 1299.99),
    (1, 2, 1, 29.99),
    (2, 3, 1, 149.99),
    (3, 4, 1, 399.99);
