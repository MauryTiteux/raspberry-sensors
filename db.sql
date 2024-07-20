CREATE TABLE logs (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    temperature FLOAT NOT NULL,
    humidity FLOAT NOT NULL,
    lux FLOAT NOT NULL,
    solar_blind_status ENUM('on', 'off'),
    script_status ENUM('on', 'off') NOT NULL,
    message VARCHAR(255) NOT NULL,
    metadata VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE settings (
    id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
    summer_opening_hour INT DEFAULT 6,
    summer_closing_hour INT DEFAULT 23,
    winter_opening_hour INT DEFAULT 7,
    winter_closing_hour INT DEFAULT 20,
    temperature_min INT DEFAULT 15,
    temperature_max INT DEFAULT 25,
    humidity_min INT DEFAULT 30,
    humidity_max INT DEFAULT 70,
    previous_lux INT DEFAULT 0,
    lux INT DEFAULT 80000,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
