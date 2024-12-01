-----------------------------------------------------------------------------------------------
--- -------------------------------- Database Setup // DDL -------------------------------- ---
-----------------------------------------------------------------------------------------------

CREATE DATABASE Home_IMS;

CREATE TABLE Home_IMS.ItemType (
  name VARCHAR(255) NOT NULL,
  unit VARCHAR(16),
  PRIMARY KEY (name)
);

CREATE TABLE Home_IMS.Consumable (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES ItemType(name)
);

CREATE TABLE Home_IMS.Durable (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES ItemType(name)
);

CREATE TABLE Home_IMS.NotFood (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Consumable(name)
);

CREATE TABLE Home_IMS.Food (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Consumable(name)
);

CREATE TABLE Home_IMS.Template (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE Home_IMS.OtherTemplate (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Template(name)
);

CREATE TABLE Home_IMS.Location (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE Home_IMS.Recipe (
  recipe_name VARCHAR(255) NOT NULL,
  food_name VARCHAR(255) NOT NULL,
  PRIMARY KEY (recipe_name, food_name),
  FOREIGN KEY (recipe_name) REFERENCES Template(name),
  FOREIGN KEY (food_name) REFERENCES Food(name)
);

CREATE TABLE Home_IMS.MealSchedule (
  recipe_name VARCHAR(255) NOT NULL,
  timestamp DATETIME NOT NULL,
  location_name VARCHAR(255) NOT NULL,
  meal_type VARCHAR(31),
  PRIMARY KEY (recipe_name, timestamp, location_name),
  FOREIGN KEY (recipe_name) REFERENCES Recipe(recipe_name),
  FOREIGN KEY (location_name) REFERENCES Location(name)
);

CREATE TABLE Home_IMS.User (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE Home_IMS.Dependent (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES User(name)
);

CREATE TABLE Home_IMS.Parent (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES User(name)
);

CREATE TABLE Home_IMS.Ingredients (
  food_name VARCHAR(255) NOT NULL,
  recipe_name VARCHAR(255) NOT NULL,
  quantity FLOAT NOT NULL,
  PRIMARY KEY (food_name, recipe_name),
  FOREIGN KEY (food_name) REFERENCES Food(name),
  FOREIGN KEY (recipe_name) REFERENCES Recipe(recipe_name),
  CHECK (quantity > 0)
);

CREATE TABLE Home_IMS.Storage (
  storage_name VARCHAR(255) NOT NULL,
  location_name VARCHAR(255) NOT NULL,
  capacity FLOAT NOT NULL,
  PRIMARY KEY (storage_name),
  FOREIGN KEY (location_name) REFERENCES Location(name),
  CHECK (capacity >= 0 AND capacity <= 2)
);

CREATE TABLE Home_IMS.Dry (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Storage(storage_name)
);

CREATE TABLE Home_IMS.Appliance (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Storage(storage_name)
);

CREATE TABLE Home_IMS.Fridge (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Appliance (name)
);

CREATE TABLE Home_IMS.Freezer (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Appliance (name)
);

CREATE TABLE Home_IMS.Inventory (
  item_name VARCHAR(255) NOT NULL,
  storage_name VARCHAR(255) NOT NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  quantity FLOAT NOT NULL,
  PRIMARY KEY (item_name, storage_name, timestamp),
  FOREIGN KEY (item_name) REFERENCES ItemType (name),
  FOREIGN KEY (storage_name) REFERENCES Storage (storage_name),
  CHECK (quantity >= 0)
);

CREATE TABLE Home_IMS.Purchase (
  item_name VARCHAR(255) NOT NULL,
  timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  quantity FLOAT NOT NULL,
  price FLOAT NOT NULL,
  store VARCHAR(255) NOT NULL,
  parent_name VARCHAR(255) NOT NULL,
  PRIMARY KEY (item_name, timestamp),
  FOREIGN KEY (parent_name) REFERENCES Parent (name),
  FOREIGN KEY (item_name) REFERENCES ItemType (name),
  CHECK (quantity > 0)
);

CREATE TABLE Home_IMS.History (
  item_name VARCHAR(255) NOT NULL,
  date_used DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  quantity FLOAT NOT NULL,
  PRIMARY KEY (item_name, date_used),
  FOREIGN KEY (item_name) REFERENCES ItemType(name),
  CHECK (quantity > 0)
);

CREATE TABLE Home_IMS.Wasted (
  item_name VARCHAR(255) NOT NULL,
  date_used DATETIME NOT NULL,
  PRIMARY KEY (item_name, date_used),
  FOREIGN KEY (item_name, date_used) REFERENCES History (item_name, date_used)
);

CREATE TABLE Home_IMS.Used (
  item_name VARCHAR(255) NOT NULL,
  date_used DATETIME NOT NULL,
  user_name VARCHAR(255),
  PRIMARY KEY (item_name, date_used),
  FOREIGN KEY (item_name, date_used) REFERENCES History (item_name, date_used),
  FOREIGN KEY (user_name) REFERENCES User (name)
);




-----------------------------------------------------------------------------------------------------------------
--- -------------------------------------- Database Queries // DML/DQL -------------------------------------- ---
-----------------------------------------------------------------------------------------------------------------


--------------------
--- MealSchedule ---
--------------------
-- Create a meal schedule --
INSERT INTO Home_IMS.MealSchedule (recipe_name, timestamp, location_name, meal_type)
VALUES (%s, %s, %s, %s);

-- Delete a meal schedule --
DELETE FROM Home_IMS.MealSchedule
WHERE recipe_name = %s
      AND timestamp = %s;

-- Select meal schedules --
SELECT recipe_name, timestamp, location_name, meal_type
FROM Home_IMS.MealSchedule
WHERE recipe_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND location_name LIKE %s
      AND meal_type LIKE %s;


----------------
--- ItemType ---
----------------
-- Add item type --
INSERT IGNORE INTO Home_IMS.ItemType (name, unit)
VALUES (%s, %s);

-- Select item type --
SELECT name, unit
FROM Home_IMS.ItemType
WHERE name LIKE %s
      AND I.unit LIKE %s;

-- TODO: Daniel I have no idea what this does --
SELECT R.recipe_name, R.food_name, M.timestamp, M.location_name, M.meal_type
FROM Home_IMS.MealSchedule AS M
JOIN Home_IMS.Recipe AS R ON M.recipe_name = R.recipe_name
WHERE R.food_name = %s;


------------------
--- Consumable ---
------------------
-- Add consumable type --
INSERT IGNORE INTO Home_IMS.Consumable (name)
VALUES (%s);

-- Select consumable type --
SELECT I.name, I.unit
FROM Home_IMS.ItemType AS I
JOIN Home_IMS.Consumable AS C ON I.name = C.name
WHERE I.name LIKE %s
      AND I.unit LIKE %s;


---------------
--- Durable ---
---------------
-- Add durable type --
INSERT IGNORE INTO Home_IMS.Durable (name)
VALUES (%s);

-- Select durable type --
SELECT I.name, I.unit
FROM Home_IMS.ItemType AS I
JOIN Home_IMS.Durable AS C ON I.name = C.name
WHERE I.name LIKE %s
      AND I.unit LIKE %s;


------------
--- Food ---
------------
-- Add food type --
INSERT IGNORE INTO Home_IMS.Food (name)
VALUES (%s);

-- Select food type --
SELECT I.name, I.unit
FROM Home_IMS.ItemType AS I
JOIN Home_IMS.Food AS C ON I.name = C.name
WHERE I.name LIKE %s
      AND I.unit LIKE %s;


---------------
--- NotFood ---
---------------
-- Add notfood type --
INSERT IGNORE INTO Home_IMS.NotFood (name)
VALUES (%s);

-- Select not food type --
SELECT I.name, I.unit
FROM Home_IMS.ItemType AS I
JOIN Home_IMS.NotFood AS C ON I.name = C.name
WHERE I.name LIKE %s
      AND I.unit LIKE %s;


----------------
--- Location ---
----------------
-- Add location --
INSERT IGNORE INTO Home_IMS.Location (name)
VALUES (%s);

-- Delete location --
DELETE FROM Home_IMS.Location
WHERE name = %s;

-- Select locations --
SELECT name
FROM Home_IMS.Location
WHERE name LIKE %s;


---------------
--- Storage ---
---------------
-- Add storage --
INSERT IGNORE INTO Home_IMS.Storage (storage_name, location_name, capacity)
VALUES (%s, %s, %s);

-- Delete storage --
DELETE FROM Home_IMS.Storage
WHERE storage_name = %s;

-- Select storage --
SELECT storage_name, location_name, capacity
FROM Home_IMS.Storage
WHERE storage_name LIKE %s
      AND location_name LIKE %s
      AND capacity BETWEEN %s AND %s;


-----------
--- Dry ---
-----------
-- Add dry storage --
INSERT IGNORE INTO Home_IMS.Dry (name)
VALUES (%s);

-- Delete dry storage --
DELETE FROM Home_IMS.Dry
WHERE name = %s;

-- Select dry storage --
SELECT S.storage_name, S.location_name, S.capacity
FROM Home_IMS.Storage as S
JOIN Home_IMS.Dry as D ON S.storage_name = D.name
WHERE S.storage_name LIKE %s
      AND S.location_name LIKE %s
      AND S.capacity BETWEEN %s AND %s;


-----------------
--- Appliance ---
-----------------
-- Add appliance storage --
INSERT IGNORE INTO Home_IMS.Appliance (name)
VALUES (%s);

-- Delete appliance storage --
DELETE FROM Home_IMS.Appliance
WHERE name = %s;

-- Select appliance storage --
SELECT S.storage_name, S.location_name, S.capacity
FROM Home_IMS.Storage as S
JOIN Home_IMS.Appliance as A ON S.storage_name = A.name
WHERE S.storage_name LIKE %s
      AND S.location_name LIKE %s
      AND S.capacity BETWEEN %s AND %s;


--------------
--- Fridge ---
--------------
-- Add fridge storage --
INSERT IGNORE INTO Home_IMS.Fridge (name)
VALUES (%s);

-- Delete fridge storage --
DELETE FROM Home_IMS.Fridge
WHERE name = %s;

-- Select fridge storage --
SELECT S.storage_name, S.location_name, S.capacity
FROM Home_IMS.Storage as S
JOIN Home_IMS.Fridge as F ON S.storage_name = F.name
WHERE S.storage_name LIKE %s
      AND S.location_name LIKE %s
      AND S.capacity BETWEEN %s AND %s;


---------------
--- Freezer ---
---------------
-- Add freezer storage --
INSERT IGNORE INTO Home_IMS.Freezer (name)
VALUES (%s);

-- Delete freezer storage --
DELETE FROM Home_IMS.Freezer
WHERE name = %s;

-- Select freezer storage --
SELECT S.storage_name, S.location_name, S.capacity
FROM Home_IMS.Storage as S
JOIN Home_IMS.Freezer as F ON S.storage_name = F.name
WHERE S.storage_name LIKE %s
      AND S.location_name LIKE %s
      AND S.capacity BETWEEN %s AND %s;


------------
--- User ---
------------
-- Add user --
INSERT IGNORE INTO Home_IMS.User (name)
VALUES (%s);

-- Select users --
SELECT name
FROM HomeIMS.User
WHERE name LIKE %s;

-- Select items used by user --
SELECT item_name, date_used
FROM Home_IMS.Used
WHERE user_name = %s;


--------------
--- Parent ---
--------------
-- Add parent --
INSERT IGNORE INTO Home_IMS.Parent (name)
VALUES (%s);


-----------------
--- Dependent ---
-----------------
-- Add dependent --
INSERT IGNORE INTO Home_IMS.Dependent (name)
VALUES (%s);


---------------
--- History ---
---------------
-- Add history record --
INSERT IGNORE INTO Home_IMS.History (item_name, quantity)
VALUES (%s, %s);


--------------
--- Wasted ---
--------------
-- Add item wasted record --
INSERT IGNORE INTO Home_IMS.Wasted (item_name, date_used)
VALUES (%s, %s);

-- Select waste records --
SELECT H.item_name, H.date_used
FROM Home_IMS.History AS H
JOIN Home_IMS.Wasted AS W
     ON H.item_name = W.item_name AND H.date_used = W.date_used
WHERE H.item_name LIKE %s
      AND H.date_used BETWEEN %s AND %s;


------------
--- Used ---
------------
-- Add item used record --
INSERT IGNORE INTO Home_IMS.Used (item_name, date_used, user_name)
VALUES (%s, %s, %s);

-- Select used records --
SELECT H.item_name, H.date_used, U.user_name
FROM Home_IMS.History AS H
JOIN Home_IMS.Used AS U
     ON H.item_name = U.item_name AND H.date_used = U.date_used
WHERE H.item_name LIKE %s
      AND H.date_used BETWEEN %s AND %s
      AND U.user_name LIKE %s;


----------------
--- Purchase ---
----------------
-- Add purchase record --
INSERT IGNORE INTO Home_IMS.Purchase (item_name, quantity, price, store, parent_name)
VALUES (%s, %s, %s, %s, %s);

-- Select purchases --
SELECT item_name, timestamp, quantity, price, store, parent_name
FROM Home_IMS.Purchase
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND item_price BETWEEN %s AND %s
      AND store LIKE %s
      AND parent_name LIKE %s;

-- Get most expensive purchase --
SELECT MAX(price) AS price
FROM Home_IMS.Purchase
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND store LIKE %s
      AND parent_name LIKE %s;

-- Get most expensive purchase price by item name --
SELECT MAX(price) AS price
FROM Home_IMS.Purchase
GROUP BY item_name
WHERE timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND store LIKE %s
      AND parent_name LIKE %s;

-- Get most expensive purchase price by parent name --
SELECT MAX(price) AS price
FROM Home_IMS.Purchase
GROUP BY parent_name
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND store LIKE %s;

-- Get most expensive purchase price by store --
SELECT MAX(price) AS price
FROM Home_IMS.Purchase
GROUP BY store
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND parent_name LIKE %s;

-- Get average purchase price --
SELECT AVG(price) AS price
FROM Home_IMS.Purchase
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND store LIKE %s
      AND parent_name LIKE %s;

-- Get average purchase price by item name --
SELECT AVG(price) AS price
FROM Home_IMS.Purchase
GROUP BY item_name
WHERE timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND store LIKE %s
      AND parent_name LIKE %s;

-- Get average purchase price by parent name --
SELECT AVG(price) AS price
FROM Home_IMS.Purchase
GROUP BY parent_name
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND store LIKE %s;

-- Get average purchase price by store --
SELECT AVG(price) AS price
FROM Home_IMS.Purchase
GROUP BY store
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND quantity BETWEEN %s AND %s
      AND parent_name LIKE %s;

-- Get total cost --
SELECT SUM(price * quantity)
FROM Home_IMS.Purchase
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND parent_name LIKE %s;


--------------
--- Recipe ---
--------------
-- Create recipe --
INSERT IGNORE INTO Home_IMS.Recipe (recipe_name, food_name)
VALUES (%s, %s);

-- Delete recipe --
DELETE FROM Home_IMS.Recipe AS R
WHERE R.recipe_name = %s
      AND R.food_name = %s;

-- View recipes --
SELECT R.recipe_name, R.food_name
FROM Home_IMS.Recipe AS R
WHERE R.recipe_name LIKE %s
      AND R.food_name LIKE %s;

-- Get estimated recipe cost --
SELECT R.recipe_name, SUM(P.avg_item_price) as cost
FROM Home_IMS.Recipe AS R, Home_IMS.Ingredients AS I,
     ( SELECT item_name, AVG(price) as avg_item_price
       FROM Home_IMS.Purchase
       GROUP BY item_name
     ) AS P
GROUP BY R.recipe_name
WHERE R.recipe_name = I.recipe_name
      AND I.food_name = P.item_name
      AND R.recipe_name LIKE %s;


-------------------
--- Ingredients ---
-------------------
-- Add ingredient --
INSERT IGNORE INTO Home_IMS.Ingredients (food_name, recipe_name, quantity)
VALUES (%s, %s, %s);

-- Remove ingredient --
DELETE FROM Home_IMS.Ingredients AS I
WHERE I.food_name = %s
      AND I.recipe_name = %s;

-- Change ingredient quantity --
UPDATE Home_IMS.Ingredients AS I
SET I.quantity = %s
WHERE I.food_name = %s
      AND I.recipe_name = %s;

-- View ingredients for a recipe --
SELECT food_name
FROM Home_IMS.Ingredients
WHERE recipe_name LIKE %s;


-----------------
--- Inventory ---
-----------------
-- Add item to inventory --
INSERT IGNORE INTO Home_IMS.Inventory (item_name, storage_name, quantity)
VALUES (%s, %s, %s);

-- Remove item from inventory --
DELETE FROM Home_IMS.Inventory AS I
WHERE I.item_name = %s
      AND I.storage_name = %s
      AND I.timestamp = %s;

-- Change item quantity --
UPDATE Home_IMS.Inventory AS I
SET I.quantity = %s
WHERE I.item_name = %s
      AND I.storage_name = %s
      AND I.timestamp = %s;

-- Move item storage location --
TODO Daniel

-- View all --
SELECT I.item_name, I.storage_name, I.timestamp, I.quantity
FROM Home_IMS.Inventory AS I
WHERE I.item_name LIKE %s
      AND I.storage_name LIKE %s
      AND I.timestamp BETWEEN %s AND %s;
