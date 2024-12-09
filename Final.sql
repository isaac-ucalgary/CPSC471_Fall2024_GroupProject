-----------------------------------------------------------------------------------------------
--- -------------------------------- Database Setup // DDL -------------------------------- ---
-----------------------------------------------------------------------------------------------

CREATE DATABASE IF NOT EXISTS Home_IMS;

CREATE TABLE IF NOT EXISTS Home_IMS.ItemType (
  name VARCHAR(255) NOT NULL,
  unit VARCHAR(16),
  PRIMARY KEY (name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Consumable (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES ItemType(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Durable (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES ItemType(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.NotFood (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Consumable(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Food (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Consumable(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Template (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.OtherTemplate (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Template(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Location (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Recipe (
  recipe_name VARCHAR(255) NOT NULL,
  PRIMARY KEY (recipe_name),
  FOREIGN KEY (recipe_name) REFERENCES Template(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.MealSchedule (
  recipe_name VARCHAR(255) NOT NULL,
  timestamp DATETIME NOT NULL,
  location_name VARCHAR(255) NOT NULL,
  meal_type VARCHAR(31),
  PRIMARY KEY (recipe_name, timestamp, location_name),
  FOREIGN KEY (recipe_name) REFERENCES Recipe(recipe_name),
  FOREIGN KEY (location_name) REFERENCES Location(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.User (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Dependent (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES User(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Parent (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES User(name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Ingredients (
  food_name VARCHAR(255) NOT NULL,
  recipe_name VARCHAR(255) NOT NULL,
  quantity FLOAT NOT NULL,
  PRIMARY KEY (food_name, recipe_name),
  FOREIGN KEY (food_name) REFERENCES Food(name),
  FOREIGN KEY (recipe_name) REFERENCES Recipe(recipe_name) ON DELETE CASCADE,
  CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Storage (
  storage_name VARCHAR(255) NOT NULL,
  location_name VARCHAR(255) NOT NULL,
  capacity FLOAT NOT NULL DEFAULT 0,
  PRIMARY KEY (storage_name),
  FOREIGN KEY (location_name) REFERENCES Location(name),
  CHECK (capacity >= 0 AND capacity <= 2)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Dry (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Storage(storage_name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Appliance (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Storage(storage_name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Fridge (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Appliance (name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Freezer (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES Appliance (name)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Inventory (
  item_name VARCHAR(255) NOT NULL,
  storage_name VARCHAR(255) NOT NULL,
  timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  expiry DATETIME,
  quantity FLOAT NOT NULL,
  PRIMARY KEY (item_name, storage_name, timestamp),
  FOREIGN KEY (item_name) REFERENCES ItemType (name),
  FOREIGN KEY (storage_name) REFERENCES Storage (storage_name),
  CHECK (quantity >= 0)
);

CREATE TABLE IF NOT EXISTS Home_IMS.Purchase (
  item_name VARCHAR(255) NOT NULL,
  timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  quantity FLOAT NOT NULL,
  price FLOAT NOT NULL,
  store VARCHAR(255) NOT NULL,
  parent_name VARCHAR(255) NOT NULL,
  PRIMARY KEY (item_name, timestamp),
  FOREIGN KEY (parent_name) REFERENCES Parent (name),
  FOREIGN KEY (item_name) REFERENCES ItemType (name),
  CHECK (quantity > 0)
);

CREATE TABLE IF NOT EXISTS Home_IMS.History (
  item_name VARCHAR(255) NOT NULL,
  timestamp DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
  quantity FLOAT NOT NULL,
  wasted BOOLEAN NOT NULL,
  user_name VARCHAR(255),
  PRIMARY KEY (item_name, timestamp),
  FOREIGN KEY (item_name) REFERENCES ItemType(name),
  CHECK (quantity > 0)
);




-----------------------------------------------------------------------------------------------------------------
--- -------------------------------------- Database Queries // DML/DQL -------------------------------------- ---
-----------------------------------------------------------------------------------------------------------------


--------------------
--- MealSchedule ---
--------------------
-- Schedule a meal --
INSERT INTO Home_IMS.MealSchedule (recipe_name, timestamp, location_name, meal_type)
VALUES (%s, %s, %s, %s);

-- Delete a meal --
DELETE FROM Home_IMS.MealSchedule
WHERE recipe_name = %s
      AND timestamp = %s;

-- Select meals --
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
INSERT INTO Home_IMS.ItemType (name, unit)
VALUES (%s, %s);

-- Select item type --
SELECT name, unit
FROM Home_IMS.ItemType
WHERE name LIKE %s
      AND unit LIKE %s;

-- TODO: Daniel I have no idea what this does --
SELECT R.recipe_name, R.food_name, M.timestamp, M.location_name, M.meal_type
FROM Home_IMS.MealSchedule AS M
JOIN Home_IMS.Recipe AS R ON M.recipe_name = R.recipe_name
WHERE R.food_name = %s;


------------------
--- Consumable ---
------------------
-- Add consumable type --
INSERT INTO Home_IMS.Consumable (name)
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
INSERT INTO Home_IMS.Durable (name)
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
INSERT INTO Home_IMS.Food (name)
VALUES (%s);

-- Select food type --
SELECT T.name, T.unit
FROM Home_IMS.ItemType AS T
JOIN Home_IMS.Food AS F ON T.name = F.name;


---------------
--- NotFood ---
---------------
-- Add notfood type --
INSERT INTO Home_IMS.NotFood (name)
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
INSERT INTO Home_IMS.Location (name)
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
INSERT INTO Home_IMS.Storage (storage_name, location_name, capacity)
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
INSERT INTO Home_IMS.Dry (name)
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
INSERT INTO Home_IMS.Appliance (name)
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
INSERT INTO Home_IMS.Fridge (name)
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
INSERT INTO Home_IMS.Freezer (name)
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
INSERT INTO Home_IMS.User (name)
VALUES (%s);

-- Select users --
SELECT name, EXISTS (
          SELECT P.name
          FROM Home_IMS.Parent AS P
          WHERE P.name = U.name
       ) AS is_parent
FROM Home_IMS.User as U
WHERE U.name LIKE %s;

-- Select items used by user --
SELECT item_name, timestamp
FROM Home_IMS.History
WHERE user_name = %s;


--------------
--- Parent ---
--------------
-- Add parent --
INSERT INTO Home_IMS.Parent (name)
VALUES (%s);

-- Select parents --
SELECT name
FROM Home_IMS.Parent
WHERE name LIKE %s;


-----------------
--- Dependent ---
-----------------
-- Add dependent --
INSERT INTO Home_IMS.Dependent (name)
VALUES (%s);


---------------
--- History ---
---------------
-- Select history records --
SELECT H.item_name, H.timestamp, H.quantity, T.unit, H.wasted, H.user_name
FROM Home_IMS.History AS H
JOIN Home_IMS.ItemType AS T ON H.item_name = T.name;

-- Select usage statistics --
SELECT H.item_name,
       T.unit,
       SUM(CASE WHEN H.wasted = false THEN H.quantity ELSE 0 END) AS amt_used,
       SUM(CASE WHEN H.wasted = true THEN H.quantity ELSE 0 END) AS amt_wasted,
       (
           SELECT IFNULL(SUM(P.price), 0)
           FROM Home_IMS.Purchase AS P
           WHERE P.item_name = H.item_name
       ) AS money_spent
FROM Home_IMS.History AS H
JOIN Home_IMS.ItemType AS T ON H.item_name = T.name
GROUP BY H.item_name;


--------------
--- Wasted ---
--------------
-- Add item wasted record --
INSERT INTO Home_IMS.History (item_name, quantity, wasted)
VALUES (%s, %s, true);

-- Select waste records --
SELECT item_name, timestamp, quantity
FROM Home_IMS.History
WHERE wasted = true
      AND item_name LIKE %s ESCAPE '!'
      AND timestamp BETWEEN %s AND %s;


------------
--- Used ---
------------
-- Add item used record --
INSERT INTO Home_IMS.History (item_name, quantity, wasted, user_name)
VALUES (%s, %s, false, %s);

-- Select used records --
SELECT item_name, timestamp, quantity, user_name
FROM Home_IMS.History
WHERE wasted = false
      AND item_name LIKE %s ESCAPE '!'
      AND timestamp BETWEEN %s AND %s
      AND user_name LIKE %s ESCAPE '!';


----------------
--- Purchase ---
----------------
-- Add purchase record --
INSERT INTO Home_IMS.Purchase (item_name, quantity, price, store, parent_name)
VALUES (%s, %s, %s, %s, %s);

-- Select purchases --
SELECT P.item_name, P.timestamp, P.quantity, T.unit, P.price, P.store, P.parent_name
FROM Home_IMS.Purchase AS P
JOIN Home_IMS.ItemType AS T ON P.item_name = T.name;

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
SELECT SUM(price)
FROM Home_IMS.Purchase
WHERE item_name LIKE %s
      AND timestamp BETWEEN %s AND %s
      AND parent_name LIKE %s;


----------------
--- Template ---
----------------
-- Create template --
INSERT INTO Home_IMS.Template (name)
VALUES (%s);


--------------
--- Recipe ---
--------------
-- Create recipe --
INSERT INTO Home_IMS.Recipe (recipe_name)
VALUES (%s);

-- Delete recipe --
DELETE FROM Home_IMS.Recipe
WHERE recipe_name = %s;

-- View recipes --
SELECT R.recipe_name
FROM Home_IMS.Recipe AS R
WHERE R.recipe_name LIKE %s ESCAPE '!';

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
INSERT INTO Home_IMS.Ingredients (recipe_name, food_name, quantity)
VALUES (%s, %s, %s);

-- Remove ingredient --
DELETE FROM Home_IMS.Ingredients
WHERE food_name = %s
      AND recipe_name = %s;

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
INSERT INTO Home_IMS.Inventory (item_name, storage_name, expiry, quantity)
VALUES (%s, %s, %s, %s);

-- Remove item from inventory --
DELETE FROM Home_IMS.Inventory
WHERE item_name = %s
      AND storage_name = %s
      AND timestamp = %s;

-- Change item quantity --
UPDATE Home_IMS.Inventory AS I
SET I.quantity = %s
WHERE I.item_name = %s
      AND I.storage_name = %s
      AND I.timestamp = %s;

-- Move item storage location --
UPDATE Home_IMS.Inventory AS I
SET I.storage_name = %s
WHERE I.item_name = %s
      AND I.storage_name = %s
      AND I.timestamp = %s;

-- View inventory items --
SELECT I.item_name, I.storage_name, S.location_name, I.timestamp, I.expiry, I.quantity, T.unit
FROM Home_IMS.Inventory AS I
JOIN Home_IMS.ItemType AS T ON I.item_name = T.name
JOIN Home_IMS.Storage AS S ON S.storage_name = I.storage_name
WHERE I.item_name LIKE %s ESCAPE '!'
      AND I.storage_name LIKE %s ESCAPE '!'
      AND (I.expiry BETWEEN %s AND %s OR (I.expiry IS NULL AND %s))
      ORDER BY ISNULL(I.expiry), I.expiry;

-- Select item quantity from inventory --
SELECT I.quantity
FROM Home_IMS.Inventory AS I
WHERE I.item_name = %s
      AND I.storage_name = %s
      AND I.timestamp = %s;


---------------------
--- Shopping List ---
---------------------
-- Select missing ingredients --
SELECT Required.food_name, Required.unit, Required.total - IFNULL(Stock.total, 0) AS quantity
FROM (
       SELECT I.food_name, T.unit, SUM(I.quantity) as total
       FROM Home_IMS.MealSchedule AS M
       JOIN Home_IMS.Ingredients AS I ON I.recipe_name = M.recipe_name
       JOIN Home_IMS.ItemType AS T ON I.food_name = T.name
       WHERE M.timestamp <= %s
       GROUP BY I.food_name
     ) AS Required
      JOIN (
       SELECT S.item_name, SUM(S.quantity) AS total
       FROM Home_IMS.Inventory AS S
       WHERE EXISTS (
               SELECT * FROM Home_IMS.MealSchedule AS M
               JOIN Home_IMS.Ingredients AS I ON M.recipe_name = I.recipe_name
               WHERE M.timestamp <= %s
                     AND I.food_name = S.item_name
             )
       GROUP BY S.item_name
     ) AS Stock ON Required.food_name = Stock.item_name
     HAVING quantity > 0;