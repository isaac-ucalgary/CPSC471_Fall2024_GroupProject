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
        PRIMARY KEY (name), 
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
        CHECK (capacity >= 0) 
    ); 
    '''
]