blog_table = """
    CREATE TABLE blog (
    id INT IDENTITY PRIMARY KEY,
    title VARCHAR(255) UNIQUE NOT NULL,
    content TEXT NOT NULL,
    image VARCHAR(MAX) NULL,
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
    image VARCHAR(MAX) NULL,
    created_at DATETIME NOT NULL,
    updated_at DATETIME NOT NULL,
    FOREIGN KEY(category_id) REFERENCES category(id));
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

update_blog_procedure = """
DROP PROCEDURE IF EXISTS UpdateBlog
CREATE PROCEDURE UpdateBlog(@title VARCHAR(255), @content TEXT, @image VARCHAR(MAX))
AS

DECLARE @blogFound int;
SET @blogFound = ISNULL ((SELECT 1 FROM blog WHERE title = @title), 0);
IF @blogFound = 1
BEGIN
    UPDATE blog 
    SET content = @content, image = @image, updated_at = GETDATE() where title = @title;
    RETURN 1;
END
ELSE
BEGIN
    RETURN 0;
END
GO
"""

insert_picture_procedure = """
CREATE PROCEDURE InsertPicture( @title VARCHAR(255), @description TEXT, @category VARCHAR(255), @image VARCHAR(max))

AS
INSERT INTO picture (title, description, category, image, created_at, updated_at)
values (@title, @description, @category, convert(varbinary, @image), GETDATE(), GETDATE());

GO
"""

drop_table_picture = "DROP TABLE IF EXISTS picture"""
drop_table_blog = "DROP TABLE IF EXISTS blog"""
drop_table_category = "DROP TABLE IF EXISTS category"""
drop_table_users = """DROP TABLE IF EXISTS users"""

stored_procedures_dict = {'InsertPicture': insert_picture_procedure}

# Order matters due to foreign key constraint
tables_to_create_in_order = [users_table, blog_table, category_table, picture_table]
tables_to_delete_in_order = [drop_table_picture, drop_table_blog, drop_table_category, drop_table_users]

