DROP DATABASE IF EXISTS Python

CREATE DATABASE Python;

USE Python;


DROP TABLE IF EXISTS User;
CREATE TABLE User (
    id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    pseudo char(100) NOT NULL UNIQUE,
    password char(30) NOT NULL,
    PRIMARY KEY (id)
)ENGINE = INNODB;


DROP TABLE IF EXISTS Product;
CREATE TABLE Product (
    id SMALLINT UNSIGNED NOT NULL AUTO_INCREMENT,
    category VARCHAR(60) NOT NULL,
    name VARCHAR(150) NOT NULL,
    labels VARCHAR(450),
    additives VARCHAR(150),
    nb_additives TINYINT,
    packagings VARCHAR(300) ,
    nutrition_grade VARCHAR(5),
    nova_group VARCHAR(5),
    traces VARCHAR(120),
    manufacturing_places_tags VARCHAR(500),
    minerals_tags VARCHAR(50),
    palm_oil VARCHAR(5),
    url VARCHAR(200),
    quantity VARCHAR(10),
    brands VARCHAR(80),
    nutriments VARCHAR(3500),
    composition VARCHAR(1800),
    PRIMARY KEY (id)
)ENGINE = INNODB;


DROP TABLE IF EXISTS Search;
CREATE TABLE Search (
    user_id SMALLINT UNSIGNED NOT NULL,
    substitute_id SMALLINT UNSIGNED NOT NULL,
    day_date TIMESTAMP,
    category CHAR(100) NOT NULL,
    product_name CHAR(100) NOT NULL,
    criterion INT,
    PRIMARY KEY (user_id, substitute_id),
    CONSTRAINT fk_sub_id FOREIGN KEY (substitute_id) REFERENCES Product(id),
    CONSTRAINT fk_usr_id FOREIGN KEY (user_id) REFERENCES User(id)
)ENGINE = INNODB;
