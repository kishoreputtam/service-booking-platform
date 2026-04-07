DROP DATABASE IF EXISTS service_booking;
CREATE DATABASE service_booking;
USE service_booking;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL
);

CREATE TABLE contact (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(150),
    message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE saved_locations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NULL,
    address VARCHAR(255) NOT NULL,
    latitude DECIMAL(10, 7) NOT NULL,
    longitude DECIMAL(10, 7) NOT NULL,
    place_id VARCHAR(255) NULL,
    source VARCHAR(30) NOT NULL DEFAULT 'manual',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_saved_locations_user
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    service_summary VARCHAR(255) NOT NULL,
    service_category VARCHAR(80) NULL,
    total_price INT NOT NULL,
    slot VARCHAR(80) NOT NULL,
    address VARCHAR(255) NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'Pending',
    assigned_professional_id INT NULL,
    professional_amount INT NOT NULL DEFAULT 0,
    admin_commission INT NOT NULL DEFAULT 0,
    work_status VARCHAR(30) NOT NULL DEFAULT 'pending',
    admin_notes TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (assigned_professional_id) REFERENCES users(id)
);

CREATE TABLE professional_profiles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(80) NOT NULL,
    years_experience INT NOT NULL DEFAULT 0,
    service_categories TEXT NOT NULL,
    about TEXT NOT NULL,
    aadhaar_number VARCHAR(20) NOT NULL,
    pan_number VARCHAR(20) NOT NULL,
    gst_number VARCHAR(20) NULL,
    bank_account_holder VARCHAR(120) NOT NULL,
    bank_account_number VARCHAR(40) NOT NULL,
    ifsc_code VARCHAR(20) NOT NULL,
    verification_status VARCHAR(20) NOT NULL DEFAULT 'pending',
    is_active BOOLEAN NOT NULL DEFAULT FALSE,
    rejection_reason TEXT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE professional_documents (
    id INT AUTO_INCREMENT PRIMARY KEY,
    professional_id INT NOT NULL,
    document_type VARCHAR(40) NOT NULL,
    filename VARCHAR(200) NOT NULL,
    data LONGBLOB NOT NULL,
    mimetype VARCHAR(100) NOT NULL,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (professional_id) REFERENCES professional_profiles(id) ON DELETE CASCADE
);

INSERT INTO users (name, email, password, role) VALUES
('Admin', 'admin@gmail.com', 'scrypt:32768:8:1$rIUZVLsu4nAZfkkg$98bce42973d41ccb4c441a56d310655cbed47342dfbeaee5e1a25771f5d3db29974b1972717c85e0449ac687876e4cdf3ccce946483d25e78b2c3e4501da5924', 'admin'),
('Provider1', 'provider@gmail.com', 'scrypt:32768:8:1$h61SW1eiCarcWN4m$914a516fa227f2c9bf73e0544bdc375310e1321adecdd0633bc3da804621681c33be4ee1f562dad7baaf17623cc592758c35b321ecad8b56f8e14bb6ed6746de', 'provider'),
('User1', 'user@gmail.com', 'scrypt:32768:8:1$8izaZ0SOlQELicZb$ac97584b306f202335a94a8d16594d5c33718cddc4be67b9f682c0a3dddbeacf7b7a34dea8e19fde6bd0f422267d730363e35c9542a747c543f364c5c7a3c782', 'user');
