blog_table = """
    CREATE TABLE blog (
    id INT IDENTITY PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    image VARBINARY(MAX) NOT NULL,
    image_format VARCHAR(50) NOT NULL,
    created_at datetime NOT NULL,
    updated_at datetime NOT NULL);
"""

category_table = """
    CREATE TABLE category (
    id INT IDENTITY PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    weight FLOAT NOT NULL,
    enabled BIT NOT NULL,
    is_subcategory BIT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL);
"""

picture_table = """
    CREATE TABLE picture (
    id INT IDENTITY PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    category_id INT NOT NULL,
    image VARBINARY(MAX) NOT NULL,
    image_format VARCHAR(50) NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY(category_id) REFERENCES category(id));
"""

favourite_pictures_table = """
    CREATE TABLE favourite_pictures (
    id INT IDENTITY PRIMARY KEY,
    picture_id INT NOT NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY(picture_id) REFERENCES picture(id)
    );
"""

users_table = """
CREATE TABLE users (
id INT IDENTITY PRIMARY KEY,
email VARCHAR(255) UNIQUE NOT NULL,
username VARCHAR(255) UNIQUE NOT NULL,
password VARCHAR(255) not null,
is_admin BIT not null,
is_verified BIT not null,
created_at DATETIME NOT NULL,
updated_at DATETIME NOT NULL);
"""


drop_favourite_pictures_table = """DROP TABLE IF EXISTS favourite_pictures"""
drop_table_picture = "DROP TABLE IF EXISTS picture"""
drop_table_blog = "DROP TABLE IF EXISTS blog"""
drop_table_category = "DROP TABLE IF EXISTS category"""
drop_table_users = """DROP TABLE IF EXISTS users"""

# Order matters due to foreign key constraint
tables_to_create_in_order = [users_table, blog_table, category_table, picture_table, favourite_pictures_table]
tables_to_delete_in_order = [drop_favourite_pictures_table, drop_table_picture, drop_table_blog, drop_table_category,
                             drop_table_users]

