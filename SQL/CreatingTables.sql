-- Users Table

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    userID INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    phoneNumber TEXT,
    address TEXT,
    created_at TIMESTAMP
);

-- Products Table
CREATE TABLE products (
    productID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    price REAL NOT NULL,
    stock INTEGER NOT NULL,
    created_at TIMESTAMP
);

-- Orders Table
CREATE TABLE orders (
    orderID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    total_amount REAL NOT NULL,
    status TEXT,
    created_at TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES users(userID)
);

-- Order Items Table
CREATE TABLE order_items (
    itemID INTEGER PRIMARY KEY AUTOINCREMENT,
    orderID INTEGER NOT NULL,
    productID INTEGER NOT NULL,
    quantity INTEGER NOT NULL,
    price REAL NOT NULL,
    FOREIGN KEY (orderID) REFERENCES orders(orderID),
    FOREIGN KEY (productID) REFERENCES products(productID)
);

-- Events Table
CREATE TABLE events (
    eventID INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    date TIMESTAMP NOT NULL,
    location TEXT,
    created_at TIMESTAMP
);

-- Bookings Table
CREATE TABLE bookings (
    bookingID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    eventID INTEGER NOT NULL,
    booking_date TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES users(userID),
    FOREIGN KEY (eventID) REFERENCES events(eventID)
);

-- Notifications Table
CREATE TABLE notifications (
    notificationID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    notificationText TEXT,
    notificationDate TIMESTAMP,
    FOREIGN KEY (userID) REFERENCES users(userID)
);

-- Instructors Table
CREATE TABLE instructors (
    instructorID INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phoneNumber TEXT,
    bio TEXT
);

-- Reviews Table
CREATE TABLE reviews (
    reviewID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    productID INTEGER NOT NULL,
    reviewText TEXT,
    rating INTEGER NOT NULL,
    socialMediaLink TEXT,
    FOREIGN KEY (userID) REFERENCES users(userID),
    FOREIGN KEY (productID) REFERENCES products(productID)
);

-- Location Table
CREATE TABLE location (
    locationID INTEGER PRIMARY KEY AUTOINCREMENT,
    locationName TEXT NOT NULL,
    locationAddress TEXT,
    locationTown TEXT,
    locationPostcode TEXT,
    locationEmail TEXT,
    locationHours TEXT
);

-- Coding Lessons Table
CREATE TABLE coding_lessons (
    lessonsID INTEGER PRIMARY KEY AUTOINCREMENT,
    userID INTEGER NOT NULL,
    lessonsDate TIMESTAMP NOT NULL,
    instructorID INTEGER NOT NULL,
    lessonsTopic TEXT NOT NULL,
    lessonsPrice REAL NOT NULL,
    FOREIGN KEY (userID) REFERENCES users(userID),
    FOREIGN KEY (instructorID) REFERENCES instructors(instructorID)
);

ALTER TABLE bookings DROP COLUMN status