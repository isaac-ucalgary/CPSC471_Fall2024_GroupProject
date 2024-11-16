-- TODO: Check that sql_statements.py uses proper foreign key hierarchy.
-- TODO: Meal/Schedule:
    -- I think Meal should contain food name and meal type, while Schedule FKs to Meal and sets a date.
    -- Consider tracking "finished" scheduled meals. If any are unfinished and past their deadline, warn user to record consumption.
    -- Maybe we should revert to a Recipe FK. If someone wants to make a singular banana into a meal, they can make a recipe.
        -- Reason: Checking for sufficient meal ingredients becomes harder otherwise. (Need to check if meal is based on recipe.)
            -- Maybe Schedule table should also have location column if we have this functionality. I won't be going to my wood shack in Manitoba to fetch tomatoes just bc they're in stock.
            -- TODO: Remove location from primary key, we now have row conflicts to worry about.
-- TODO: Timestamp problems (I can't believe y2k38 is something I actually have to think about.)
-- TODO: Investigate SQL transactions to avoid race conditions.
-- TODO: Record any schema changes before submitting deliverable on Sunday.
-- TODO: Don't forget ordering in [any SQL statements]/[any functionality (471.yml)].
-- NOTE: execute("SELECT * FROM sometable WHERE item LIKE "%s" AND user LIKE "%s", "%", "dane")
    -- NOTENOTE: With this, we don't have to write out multiple variants of the same sql statement.
              -- If sorting, then we'd have 2 (or 6) different variants.
-- TODO: Use mysql.connector.Error.errno to detect foreign key failures.
-- TODO: Do we want pruning for Inventory?
-- TODO: Find any SELECT * then decide what columns to query.
-- TODO: Handle user permissions app-side.

- "Grouping items by type."
- "No expiry date, best before date may not be expired, could display product age instead."

--- MealSchedule

- INSERT INTO Home_IMS.MealSchedule (recipe_name, timestamp, location_name, meal_type)
  VALUES (%s, %s, %s, %s);

- DELETE FROM Home_IMS.MealSchedule
  WHERE recipe_name = %s
  AND timestamp = %s;

- SELECT recipe_name, timestamp, location_name, meal_type FROM Home_IMS.MealSchedule
  WHERE recipe_name LIKE %s
  AND timestamp BETWEEN %s AND %s
  AND location_name LIKE %s
  AND meal_type LIKE %s;

-- TODO Sufficient ingredients check.
-- TODO Consumption queries.

--- ItemType

- INSERT INTO Home_IMS.ItemType (name, unit)
  VALUES (%s, %s);

- INSERT INTO Home_IMS.Consumable (name)
  VALUES (%s, %s);

- INSERT INTO Home_IMS.Durable (name)
  VALUES (%s, %s);

- INSERT INTO Home_IMS.Food (name)
  VALUES (%s, %s);

- INSERT INTO Home_IMS.NotFood (name)
  VALUES (%s, %s);

- SELECT name, unit FROM Home_IMS.ItemType
  WHERE name LIKE %s;

- SELECT I.name, I.unit FROM Home_IMS.ItemType AS I
  JOIN Home_IMS.Consumable AS C ON I.name = C.name
  WHERE name LIKE %s;

- SELECT I.name, I.unit FROM Home_IMS.ItemType
  JOIN Home_IMS.Durable AS C ON I.name = C.name
  WHERE name LIKE %s;

- SELECT I.name, I.unit FROM Home_IMS.ItemType
  JOIN Home_IMS.Food AS C ON I.name = C.name
  WHERE name LIKE %s;

- SELECT I.name, I.unit FROM Home_IMS.ItemType
  JOIN Home_IMS.NotFood AS C ON I.name = C.name;
  WHERE name LIKE %s;

-- TODO M.<column_name>
- SELECT * FROM Home_IMS.MealSchedule AS M
  JOIN Home_IMS.Recipe AS R ON M.recipe_name = R.recipe_name
  WHERE R.food_name = %s;

--- Location

- INSERT INTO Home_IMS.Location (name)
  VALUES (%s);

- DELETE FROM Home_IMS.Location
  WHERE name = %s;

- SELECT name FROM Home_IMS.Location 
  WHERE name LIKE %s;

--- Storage (+ subclasses)

- INSERT INTO Home_IMS.Storage (storage_name, location_name)
  VALUES (%s, %s);

- INSERT INTO Home_IMS.Dry (name)
  VALUES (%s);

- INSERT INTO Home_IMS.Appliance (name)
  VALUES (%s);

- INSERT INTO Home_IMS.Fridge (name)
  VALUES (%s);

- INSERT INTO Home_IMS.Freezer (name)
  VALUES (%s);

- DELETE FROM Home_IMS.Storage
  WHERE storage_name = %s;

- DELETE FROM Home_IMS.Dry
  WHERE name = %s;

- DELETE FROM Home_IMS.Appliance
  WHERE name = %s;

- DELETE FROM Home_IMS.Fridge
  WHERE name = %s;

- DELETE FROM Home_IMS.Freezer
  WHERE name = %s;

-- TODO Do we need to select capacity?
- SELECT storage_name, location_name FROM Home_IMS.Storage
  WHERE storage_name LIKE %s
  AND location_name LIKE %s;

- SELECT S.storage_name, S.location_name FROM Home_IMS.Storage as S
  JOIN Home_IMS.Dry as D ON S.storage_name = D.name
  WHERE storage_name LIKE %s
  AND location_name LIKE %s;

- SELECT S.storage_name, S.location_name FROM Home_IMS.Storage as S
  JOIN Home_IMS.Appliance as A ON S.storage_name = A.name
  WHERE storage_name LIKE %s
  AND location_name LIKE %s;

- SELECT S.storage_name, S.location_name FROM Home_IMS.Storage as S
  JOIN Home_IMS.Fridge as F ON S.storage_name = F.name
  WHERE storage_name LIKE %s
  AND location_name LIKE %s;

- SELECT S.storage_name, S.location_name FROM Home_IMS.Storage as S
  JOIN Home_IMS.Freezer as F ON S.storage_name = F.name
  WHERE storage_name LIKE %s
  AND location_name LIKE %s;

--- User (+ subclasses)

- INSERT INTO Home_IMS.User (name)
  VALUES (%s);

- INSERT INTO Home_IMS.Parent (name)
  VALUES (%s);

- INSERT INTO Home_IMS.Dependent (name)
  VALUES (%s);

- SELECT name from HomeIMS.User
  WHERE name LIKE %s;

- SELECT item_name, date_used FROM Home_IMS.Used
  WHERE user_name = %s;

--- History (+ subclasses)

- INSERT INTO Home_IMS.History (item_name, quantity)
  VALUES (%s, %s);

- INSERT INTO Home_IMS.Wasted (item_name, date_used)
  VALUES (%s, %s);

- INSERT INTO Home_IMS.Used (item_name, date_used, user_name)
  VALUES (%s, %s, %s);

-- TODO: Filter by quantity?
- SELECT H.item_name, H.date_used FROM Home_IMS.History AS H
  JOIN Home_IMS.Wasted AS W ON H.item_name = W.item_name AND H.date_used = W.date_used
  WHERE H.item_name LIKE %s
  AND H.date_used BETWEEN %s AND %s;

-- TODO: Filter by quantity?
- SELECT H.item_name, H.date_used, U.user_name FROM Home_IMS.History AS H
  JOIN Home_IMS.Used AS U ON H.item_name = U.item_name AND H.date_used = U.date_used
  WHERE H.item_name LIKE %s
  AND H.date_used BETWEEN %s AND %s
  AND U.user_name LIKE %s;

-- TODO May need something like SELECT name, unit FROM ItemType NATURAL JOIN Food;

--- SELECT food_name, quantity FROM Home_IMS.Ingredients WHERE recipe_name = %s;
--- SELECT recipe_name FROM Home_IMS.Recipe;


--- SELECT name FROM Home_IMS.Location;
--- SELECT I.item_name, I.timestamp, I.quantity, T.unit FROM Home_IMS.Inventory AS I
  --JOIN Home_IMS.ItemType AS T ON I.item_name = T.name
  --WHERE storage_name = %s
  --ORDER BY item_name ASC, timestamp ASC; -- Default ORDER BY clause for now. We'll talk about this later.

--- SELECT recipe_name FROM Home_IMS.Ingredients WHERE food_name LIKE %s ESCAPE '!'; -- Possibly useful.
---- TODO Select recipes based on inventory.

--- UPDATE Home_IMS.Ingredients SET quantity = %s WHERE food_name = %s AND recipe_name = %s;
--- UPDATE Home_IMS.Storage SET capacity = %s WHERE storage_name = %s AND location_name = %s;

--- INSERT INTO Home_IMS.Storage (storage_name, location_name) VALUES (%s, %s);
--- INSERT INTO Home_IMS.Inventory (item_name, storage_name, timestamp, quantity) VALUES (%s, %s, %s, %s) ON DUPLICATE KEY UPDATE quantity = %s;
