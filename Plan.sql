----------------------
--- Database setup ---
----------------------

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
  FOREIGN KEY (name) REFERENCES ItemType(name)
);

CREATE TABLE Home_IMS.Food (
  name VARCHAR(255) NOT NULL,
  PRIMARY KEY (name),
  FOREIGN KEY (name) REFERENCES ItemType(name)
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
  meal_type VARCHAR(31),
  PRIMARY KEY (recipe_name, timestamp),
  FOREIGN KEY (recipe_name) REFERENCES Recipe(recipe_name)
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
  expiry DATETIME,
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

--------------------
--- MealSchedule ---
--------------------

INSERT INTO Home_IMS.MealSchedule (recipe_name, timestamp, meal_type)
VALUES (%s, %s, %s, %s);

DELETE FROM Home_IMS.MealSchedule
WHERE recipe_name = %s
AND timestamp = %s;

SELECT recipe_name, timestamp, meal_type FROM Home_IMS.MealSchedule
WHERE recipe_name LIKE %s ESCAPE '!'
AND timestamp BETWEEN %s AND %s
AND meal_type LIKE %s ESCAPE '!';

-----------------
--- Item type ---
-----------------

-- Add item type
INSERT INTO Home_IMS.ItemType (name, unit)
VALUES (%s, %s);

INSERT INTO Home_IMS.Consumable (name)
VALUES (%s, %s);

INSERT INTO Home_IMS.Durable (name)
VALUES (%s, %s);

INSERT INTO Home_IMS.Food (name)
VALUES (%s, %s);

INSERT INTO Home_IMS.NotFood (name)
VALUES (%s, %s);

-- Search item types (by name and type)
SELECT name, unit FROM Home_IMS.ItemType
WHERE name LIKE %s ESCAPE '!';

SELECT I.name, I.unit FROM Home_IMS.ItemType AS I
JOIN Home_IMS.Consumable AS C ON I.name = C.name
WHERE name LIKE %s ESCAPE '!';

SELECT I.name, I.unit FROM Home_IMS.ItemType
JOIN Home_IMS.Durable AS C ON I.name = C.name
WHERE name LIKE %s ESCAPE '!';

SELECT I.name, I.unit FROM Home_IMS.ItemType
JOIN Home_IMS.Food AS C ON I.name = C.name
WHERE name LIKE %s ESCAPE '!';

SELECT I.name, I.unit FROM Home_IMS.ItemType
JOIN Home_IMS.NotFood AS C ON I.name = C.name;
WHERE name LIKE %s ESCAPE '!';

----------------
--- Location ---
----------------

-- Add location
INSERT INTO Home_IMS.Location (name)
VALUES (%s);

-- Remove location
DELETE FROM Home_IMS.Location
WHERE name = %s;

-- Search (by name)
SELECT name FROM Home_IMS.Location 
WHERE name LIKE %s ESCAPE '!';

---------------
--- Storage ---
---------------

-- Add storage
INSERT INTO Home_IMS.Storage (storage_name, location_name)
VALUES (%s, %s);

INSERT INTO Home_IMS.Dry (name)
VALUES (%s);

INSERT INTO Home_IMS.Appliance (name)
VALUES (%s);

INSERT INTO Home_IMS.Fridge (name)
VALUES (%s);

INSERT INTO Home_IMS.Freezer (name)
VALUES (%s);

-- Remove storage
DELETE FROM Home_IMS.Storage
WHERE storage_name = %s;

DELETE FROM Home_IMS.Dry
WHERE name = %s;

DELETE FROM Home_IMS.Appliance
WHERE name = %s;

DELETE FROM Home_IMS.Fridge
WHERE name = %s;

DELETE FROM Home_IMS.Freezer
WHERE name = %s;

-- Update capacity estimate
UPDATE Home_IMS.Storage
SET capacity = %s
WHERE storage_name = %s;

-- Search available storages (by name, location and type)
SELECT storage_name, location_name, capacity FROM Home_IMS.Storage
WHERE storage_name LIKE %s ESCAPE '!'
AND location_name LIKE %s ESCAPE '!';

SELECT S.storage_name, S.location_name, S.capacity FROM Home_IMS.Storage as S
JOIN Home_IMS.Dry as D ON S.storage_name = D.name
WHERE storage_name LIKE %s ESCAPE '!'
AND location_name LIKE %s ESCAPE '!';

SELECT S.storage_name, S.location_name, S.capacity FROM Home_IMS.Storage as S
JOIN Home_IMS.Appliance as A ON S.storage_name = A.name
WHERE storage_name LIKE %s ESCAPE '!'
AND location_name LIKE %s ESCAPE '!';

SELECT S.storage_name, S.location_name, S.capacity FROM Home_IMS.Storage as S
JOIN Home_IMS.Fridge as F ON S.storage_name = F.name
WHERE storage_name LIKE %s ESCAPE '!'
AND location_name LIKE %s ESCAPE '!';

SELECT S.storage_name, S.location_name, S.capacity FROM Home_IMS.Storage as S
JOIN Home_IMS.Freezer as F ON S.storage_name = F.name
WHERE storage_name LIKE %s ESCAPE '!'
AND location_name LIKE %s ESCAPE '!';

------------
--- User ---
------------

-- Add user
INSERT INTO Home_IMS.User (name)
VALUES (%s);

INSERT INTO Home_IMS.Parent (name)
VALUES (%s);

INSERT INTO Home_IMS.Dependent (name)
VALUES (%s);

-- Search user (by name)
SELECT name from Home_IMS.User
WHERE name LIKE %s ESCAPE '!';

-- View user consumption records
SELECT item_name, date_used FROM Home_IMS.Used
WHERE user_name = %s;

-- View user purchase records
SELECT item_name, timestamp, quantity, price, store FROM Home_IMS.Purchase
WHERE parent_name = %s;

---------------
--- History ---
---------------

-- Record usage
INSERT INTO Home_IMS.History (item_name, quantity)
VALUES (%s, %s);

INSERT INTO Home_IMS.Wasted (item_name, date_used)
VALUES (%s, %s);

INSERT INTO Home_IMS.Used (item_name, date_used, user_name)
VALUES (%s, %s, %s);

-- Search usage history (by item type, date range and usage type)
SELECT item_name, date_used, quantity FROM Home_IMS.History
WHERE item_name LIKE %s ESCAPE '!'
AND date_used BETWEEN %s AND %s;

-- TODO: Filter by quantity?
SELECT H.item_name, H.date_used, H.quantity FROM Home_IMS.History AS H
JOIN Home_IMS.Wasted AS W ON H.item_name = W.item_name AND H.date_used = W.date_used
WHERE H.item_name LIKE %s ESCAPE '!'
AND H.date_used BETWEEN %s AND %s;

-- TODO: Filter by quantity?
SELECT H.item_name, H.date_used, H.quantity, U.user_name FROM Home_IMS.History AS H
JOIN Home_IMS.Used AS U ON H.item_name = U.item_name AND H.date_used = U.date_used
WHERE H.item_name LIKE %s ESCAPE '!'
AND H.date_used BETWEEN %s AND %s
AND U.user_name LIKE %s ESCAPE '!';

----------------
--- Purchase ---
----------------

-- Record purchase
INSERT INTO Home_IMS.Purchase (item_name, quantity, price, store, parent_name)
VALUES (%s, %s, %s, %s, %s);

-- Search purchases (by item type, time of purchase, store name and parent name)
-- TODO Filter by quantity/price?
SELECT item_name, timestamp, quantity, price, store, parent_name FROM Home_IMS.Purchase
WHERE item_name LIKE %s ESCAPE '!'
AND timestamp BETWEEN %s AND %s
AND store LIKE %s ESCAPE '!'
AND parent_name LIKE %s ESCAPE '!';

--------------
--- Recipe ---
--------------

-- Create recipe
INSERT INTO Home_IMS.Recipe (recipe_name, food_name)
VALUES (%s, %s);

-- Delete recipe
DELETE FROM Home_IMS.Recipe
WHERE recipe_name = %s
AND food_name = %s;

-- Search (by recipe name and ingredient)
SELECT R.recipe_name FROM Home_IMS.Recipe AS R
WHERE R.recipe_name LIKE %s ESCAPE '!'
AND EXISTS (
  SELECT * FROM Home_IMS.Ingredients AS I
  WHERE I.recipe_name = R.recipe_name
  AND I.food_name LIKE %s ESCAPE '!'
);

-------------------
--- Ingredients ---
-------------------

-- Add ingredient to recipe
INSERT INTO Home_IMS.Ingredients (food_name, recipe_name, quantity)
VALUES (%s, %s, %s);

-- Remove ingredient from recipe
DELETE FROM Home_IMS.Ingredients
WHERE food_name = %s
AND recipe_name = %s;

-- Change ingredient quantity in recipe
UPDATE Home_IMS.Ingredients
SET quantity = %s
WHERE recipe_name = %s
AND food_name = %s;

-- View all recipe ingredients
SELECT food_name, quantity FROM Home_IMS.Ingredients
WHERE recipe_name = %s
AND food_name = %s;

-----------------
--- Inventory ---
-----------------

-- Add inventory
INSERT INTO Home_IMS.Inventory (item_name, storage_name, expiry, quantity)
VALUES (%s, %s, %s, %s);

-- Remove inventory
DELETE FROM Home_IMS.Inventory
WHERE item_name = %s
AND storage_name = %s
AND timestamp = %s;

-- Change inventory quantity
UPDATE Home_IMS.Inventory
SET quantity = %s
WHERE item_name = %s
AND storage_name = %s
AND timestamp = %s;

-- Move inventory between storage (coupled with an inventory removal)
INSERT INTO Home_IMS.Inventory (item_name, storage_name, timestamp, expiry, quantity)
VALUES (%s, %s, %s, %s, %s:@old_quantity)
ON DUPLICATE KEY UPDATE quantity = quantity + %s:@old_quantity;

-- Search inventory (by item type, time added, expiry, storage and location)
SELECT I.item_name, I.storage_name, I.timestamp, I.expiry, I.quantity, T.units FROM Home_IMS.Inventory AS I
JOIN Home_IMS.Storage AS S ON I.storage_name = S.storage_name
JOIN Home_IMS.ItemType AS T on I.item_name = T.name
WHERE I.item_name LIKE %s ESCAPE '!'
AND I.timestamp BETWEEN %s AND %s
AND I.expiry BETWEEN %s AND %s
AND I.storage_name LIKE %s ESCAPE '!'
AND S.location_name LIKE %s ESCAPE '!';

-----------------
--- Analytics ---
-----------------

-- Get total quantity used per item type (filtered by item type)
SELECT H.item_name, SUM(H.quantity) FROM Home_IMS.History AS H
JOIN Home_IMS.Used AS U ON U.item_name = H.item_name AND U.date_used = H.date_used
WHERE H.item_name LIKE %s ESCAPE '!'
GROUP BY H.item_name;

-- Get total quantity wasted per item type (filtered by item type)
SELECT H.item_name, SUM(H.quantity) FROM Home_IMS.History AS H
JOIN Home_IMS.Wasted AS W ON W.item_name = H.item_name AND W.date_used = H.date_used
WHERE H.item_name LIKE %s ESCAPE '!'
GROUP BY H.item_name;

-- Get total expenditure per item type (filtered by item type)
SELECT item_name, SUM(price) FROM Home_IMS.Purchase
WHERE item_name LIKE %s ESCAPE '!'
GROUP BY item_name;

---------------------
--- Shopping list ---
---------------------

-- Get total ingredients needed for meals scheduled no later than provided date.
SELECT I.food_name, SUM(I.quantity) AS total_quantity FROM Home_IMS.MealSchedule AS M
JOIN Home_IMS.Ingredients AS I ON I.recipe_name = M.recipe_name
WHERE M.timestamp <= %s
GROUP BY I.food_name;

-- Get total stock for ingredients needed in meals scheduled no later than provided date.
SELECT S.item_name, SUM(quantity) AS total_quantity FROM Home_IMS.Inventory
AND EXISTS (
  SELECT * FROM Home_IMS.MealSchedule AS M
  JOIN Home_IMS.Ingredients AS I ON M.recipe_name = I.recipe_name
  WHERE M.timestamp <= %s
  AND I.food_name = S.item_name
)
GROUP BY item_name;
