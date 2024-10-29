sql_tables = [

    '''
    CREATE TABLE ItemType ( 
        name VARCHAR(255) NOT NULL, 
        unit VARCHAR(16), 
        PRIMARY KEY (name) 
    );
    ''',

    '''
    CREATE TABLE Consumable ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name), 
        FOREIGN KEY (name) REFERENCES ItemType(name) 
    ); 
    ''',

    '''
    CREATE TABLE Durable ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name), 
        FOREIGN KEY (name) REFERENCES ItemType(name) 
    ); 
    ''',

    '''
    CREATE TABLE NotFood ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name), 
        FOREIGN KEY (name) REFERENCES ItemType(name) 
    ); 
    ''',

    '''
    CREATE TABLE Food ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name), 
        FOREIGN KEY (name) REFERENCES ItemType(name) 
    ); 
    ''',

    '''
    CREATE TABLE Template ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name) 
    ); 
    ''',

    '''
    CREATE TABLE OtherTemplate ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name), 
        FOREIGN KEY (name) REFERENCES Template(name)
    );
    ''',

    '''
    CREATE TABLE Recipe ( 
        recipe_name VARCHAR(255) NOT NULL, 
        food_name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (recipe_name, food_name), 
        FOREIGN KEY (recipe_name) REFERENCES Template(name), 
        FOREIGN KEY (food_name) REFERENCES Food(name) 
    );
    ''',

    '''
    CREATE TABLE Meal ( 
        id INT NOT NULL AUTO_INCREMENT, 
        meal_type VARCHAR(16), 
        date DATE NOT NULL, 
        PRIMARY KEY (id) 
    ); 
    ''',

    '''
    CREATE TABLE User ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name) 
    ); 
    ''',

    '''
    CREATE TABLE Dependent ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name),
        FOREIGN KEY (name) REFERENCES User (name)
    ); 
    ''',

    '''
    CREATE TABLE Parent ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name),
        FOREIGN KEY (name) REFERENCES User (name)
    ); 
    ''',

    '''
    CREATE TABLE Location ( 
        name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (name) 
    ); 
    ''',

    '''
    CREATE TABLE Schedule ( 
        meal_id INT NOT NULL, 
        food_name VARCHAR(255) NOT NULL, 
        PRIMARY KEY (meal_id, food_name), 
        FOREIGN KEY (meal_id) REFERENCES Meal(id), 
        FOREIGN KEY (food_name) REFERENCES Food(name) 
    );
    ''',

    '''
    CREATE TABLE Ingredients ( 
        food_name VARCHAR(255) NOT NULL, 
        recipe_name VARCHAR(255) NOT NULL, 
        quantity FLOAT NOT NULL, 
        PRIMARY KEY (food_name, recipe_name), 
        FOREIGN KEY (food_name) REFERENCES Food(name), 
        FOREIGN KEY (recipe_name) REFERENCES Recipe(name), 
        CHECK (quantity > 0) 
    ); 
    ''',

    '''
    CREATE TABLE Storage ( 
        storage_name VARCHAR(255) NOT NULL, 
        location_name VARCHAR(255) NOT NULL, 
        capacity FLOAT NOT NULL, 
        PRIMARY KEY (storage_name), 
        FOREIGN KEY (location_name) REFERENCES Location(name), 
        CHECK (capacity >= 0 AND capacity <= 2) 
    ); 
    ''',

    '''
    CREATE TABLE Dry (
        name VARCHAR(255) NOT NULL,
        PRIMARY KEY (name),
        FOREIGN KEY (name) REFERENCES Storage(storage_name)
    );
    ''',

    '''
    CREATE TABLE Appliance (
        name VARCHAR(255) NOT NULL,
        PRIMARY KEY (name),
        FOREIGN KEY (name) REFERENCES Storage(storage_name)
    );
    ''',

    '''
    CREATE TABLE Fridge (
        name VARCHAR(255) NOT NULL,
        PRIMARY KEY (name),
        FOREIGN KEY (name) REFERENCES Appliance (name)
    );
    ''',

    '''
    CREATE TABLE Freezer (
        name VARCHAR(255) NOT NULL,
        PRIMARY KEY (name),
        FOREIGN KEY (name) REFERENCES Appliance (name)
    );
    ''', 

    '''
    CREATE TABLE Inventory (
        item_name VARCHAR(255) NOT NULL,
        storage_name VARCHAR(255) NOT NULL,  
        quantity FLOAT NOT NULL,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (item_name, storage_name, timestamp),
        FOREIGN KEY (item_name) REFERENCES ItemType (name),
        FOREIGN KEY (storage_name) REFERENCES Storage (storage_name),
        CHECK (quantity >= 0)  
    );
    ''', #:)

    '''
    CREATE TABLE Purchase (
        item_name VARCHAR(255) NOT NULL,
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        quantity FLOAT NOT NULL,
        price FLOAT NOT NULL,
        store VARCHAR(255) NOT NULL,
        parent_name VARCHAR(255) NOT NULL,
        PRIMARY KEY (item_name, timestamp),
        FOREIGN KEY (parent_name) REFERENCES Parent (name), 
        FOREIGN KEY (item_name) REFERENCES ItemType (name),
        CHECK (quantity > 0)
    );
    ''',

    '''
    CREATE TABLE History (
        item_name VARCHAR(255) NOT NULL,
        date_used TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        quantity FLOAT NOT NULL,
        PRIMARY KEY (item_name, date_used),
        FOREIGN KEY (item_name),
        CHECK (quantity > 0) 
    );
    ''',

    '''
    CREATE TABLE Wasted (
        item_name VARCHAR(255) NOT NULL,
        date_used TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        PRIMARY KEY (item_name, date_used),
        FOREIGN KEY (item_name) REFERENCES History (item_name),
        FOREIGN KEY (date_used) REFERENCES History (date_used),
        CHECK (quantity > 0) 
    );
    ''',

    '''
    CREATE TABLE Used (
        item_name VARCHAR(255) NOT NULL,
        date_used TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        user_name VARCHAR(255),
        PRIMARY KEY (item_name, date_used),
        FOREIGN KEY (item_name) REFERENCES History (item_name),
        FOREIGN KEY (date_used) REFERENCES History (date_used),
        FOREIGN KEY (user_name) REFERENCES User (name),
        CHECK (quantity > 0) 
    );
    '''
]