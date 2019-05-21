/* drop and create db */
DROP DATABASE IF EXISTS treoplan;
CREATE DATABASE treoplan CHARACTER SET utf8mb4 COLLATE utf8mb4_bin;
USE treoplan;

/* drop tables */
DROP TABLE IF EXISTS treoplan_product;
DROP TABLE IF EXISTS treoplan_image;

/* create treoplan_product table */
CREATE TABLE treoplan_product (
    articul varchar(255) NOT NULL PRIMARY KEY,
    name TEXT NULL,
    id varchar(255) NULL,
    prid varchar(255) NULL,
    vendor varchar(255) NULL,
    currency varchar(255) NULL,
    freenom varchar(255) NULL,
    price DECIMAL(20,2) NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT FALSE,
    CONSTRAINT unique_idx_articul UNIQUE (articul)
);

/* create treoplan_image table */
CREATE TABLE treoplan_image (
    id INTEGER NOT NULL PRIMARY KEY AUTO_INCREMENT,
    url varchar(255) NOT NULL,
    articul varchar(255) NULL
);

/* create index on foreign key treoplan_image(product_sku) */
CREATE INDEX treoplan_image_articul_idx ON treoplan_image(articul);
