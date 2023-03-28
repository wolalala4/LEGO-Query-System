CREATE DATABASE lego;

USE lego;

CREATE TABLE themes (
	tid INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE sets (
	sid INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    releaseYear YEAR,
    partNum INT DEFAULT 0,
    numLeft INT DEFAULT 0,
    price DECIMAL(6,2) NOT NULL,
    tid INT,
    
    CONSTRAINT fk_sets_themes FOREIGN KEY (tid)
		REFERENCES themes(tid)
		ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE color (
	name VARCHAR(50) PRIMARY KEY,
    rgb VARCHAR(50) UNIQUE NOT NULL,
    transparent TINYINT
);

CREATE TABLE categories (
	catId INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE parts (
	pid INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) UNIQUE NOT NULL,
    numLeft INT DEFAULT 0,
    price DECIMAL(6,2) NOT NULL,
    cname VARCHAR(50),
    catId INT,
    
    CONSTRAINT fk_parts_color FOREIGN KEY (cname)
		REFERENCES color(name)
        ON DELETE CASCADE ON UPDATE CASCADE,
        
	CONSTRAINT fk_parts_category FOREIGN KEY (catId)
		REFERENCES categories(catId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Address(
    zipCode VARCHAR(10) PRIMARY KEY,
    city VARCHAR(20) NOT NULL,
    state CHAR(2) NOT NULL
);

CREATE TABLE Branches(
    cid INT PRIMARY KEY AUTO_INCREMENT,
    branchName VARCHAR(30) UNIQUE NOT NULL,
    profit DECIMAL(9,2) DEFAULT 0,
    zipCode VARCHAR(10),
    
    CONSTRAINT fk_Branches_Address FOREIGN KEY(zipCode)
        REFERENCES Address(zipCode)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE Staff(
    staffId INT PRIMARY KEY AUTO_INCREMENT,
    staffName VARCHAR(40) UNIQUE NOT NULL,
    staffPassword VARCHAR(40) NOT NULL,
    staffSalary INT DEFAULT 0,
    cid INT,
    
    CONSTRAINT fk_Staff_Branches FOREIGN KEY(cid)
		REFERENCES Branches(cid)
		ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE part_restock (
	restockId INT PRIMARY KEY AUTO_INCREMENT,
    rDate DATE NOT NULL,
    staffId INT,
    
    CONSTRAINT fk_part_restock_staff FOREIGN KEY (staffId)
		REFERENCES Staff(staffId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE set_restock (
	restockId INT PRIMARY KEY AUTO_INCREMENT,
    sDate DATE NOT NULL,
    staffId INT,
    
    CONSTRAINT fk_set_restock_staff FOREIGN KEY (staffId)
		REFERENCES Staff(staffId)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE part_restock_detail (
	restockId INT,
    pid INT,
    quatity INT DEFAULT 0,
    
    PRIMARY KEY (restockId, pid),
    
    CONSTRAINT fk_part_restock_records_rp FOREIGN KEY (restockId)
		REFERENCES part_restock(restockId)
        ON DELETE CASCADE ON UPDATE CASCADE,
        
	CONSTRAINT fk_part_restock_records_p FOREIGN KEY (pid)
		REFERENCES parts(pid)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE set_restock_detail (
	restockId INT,
    sid INT,
    quatity INT DEFAULT 0,
    
    PRIMARY KEY (restockId, sid),
    
    CONSTRAINT fk_part_restock_records_rs FOREIGN KEY (restockId)
		REFERENCES set_restock(restockId)
        ON DELETE CASCADE ON UPDATE CASCADE,
        
	CONSTRAINT fk_part_restock_records_s FOREIGN KEY (sid)
		REFERENCES sets(sid)
        ON DELETE CASCADE ON UPDATE CASCADE
);

CREATE TABLE Customer(
    customerEmail VARCHAR(50) PRIMARY KEY,
    customerName VARCHAR(20) NOT NULL,
    balance DECIMAL(6,2) NOT NULL,
    zipCode VARCHAR(10),
    
    CONSTRAINT fk_customer_address FOREIGN KEY(zipCode)
		REFERENCES Address(zipCode)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE sets_order
(
    cid INT,
    customerEmail VARCHAR(50),
    businessTime DATETIME,
    quantity INT NOT NULL,
    sid INT,
    
    PRIMARY KEY (cid, customerEmail, businessTime, sid),
    
    CONSTRAINT fk_sets_order_Branches FOREIGN KEY (cid)
		REFERENCES Branches(cid)
        ON UPDATE CASCADE ON DELETE CASCADE,
        
    CONSTRAINT fk_sets_order_Customer FOREIGN KEY (customerEmail)
		REFERENCES Customer(customerEmail)
        ON UPDATE CASCADE ON DELETE CASCADE,
        
	CONSTRAINT fk_sets_order_Sets FOREIGN KEY (sid)
		REFERENCES sets(sid)
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE parts_order
(
    cid INT,
    customerEmail VARCHAR(50),
    businessTime DATETIME,
    quantity INT NOT NULL,
    pid INT,
    
    PRIMARY KEY (cid, customerEmail, businessTime, pid),
    
    CONSTRAINT fk_parts_order_Branches FOREIGN KEY (cid)
		REFERENCES Branches(cid)
        ON UPDATE CASCADE ON DELETE CASCADE,
        
    CONSTRAINT fk_parts_order_Customer FOREIGN KEY (customerEmail)
		REFERENCES Customer(customerEmail)
        ON UPDATE CASCADE ON DELETE CASCADE,
        
	CONSTRAINT fk_parts_order_Sets FOREIGN KEY (pid)
		REFERENCES parts(pid)
        ON UPDATE CASCADE ON DELETE CASCADE
);


DELIMITER $$
CREATE PROCEDURE find_customer_by_email(
	email VARCHAR(50)
)
BEGIN
	SELECT * FROM customer WHERE customerEmail = email;
END $$

DELIMITER $$
CREATE PROCEDURE add_customer(
	email VARCHAR(50),
    name VARCHAR(20),
    balance DECIMAL(6,2),
    zipCode VARCHAR(10)
)
BEGIN
	DECLARE data_duplicate TINYINT DEFAULT FALSE;
    DECLARE zipCode_not_found TINYINT DEFAULT FALSE;
    DECLARE CONTINUE HANDLER FOR 1062
		SET data_duplicate = TRUE;
	DECLARE CONTINUE HANDLER FOR 1452
		SET zipCode_not_found = TRUE;
	INSERT INTO customer VALUES (email, name, balance, zipCode);
    IF data_duplicate = TRUE THEN
		SELECT 'Register failed! This customer has already exists!';
	END IF;
    IF zipCode_not_found = TRUE THEN
		SELECT 'Register failed! zipCode not found!';
    END IF;
    IF data_duplicate = FALSE AND zipCode_not_found = FALSE THEN
		SELECT 'Register success!';
	END IF;
END $$

DELIMITER $$
CREATE FUNCTION set_total_price(
	setPrice DECIMAL(6,2),
    quantity INT
)
RETURNS DECIMAL(6,2)
DETERMINISTIC NO SQL
BEGIN
	RETURN setPrice * quantity;
END $$

DELIMITER $$
CREATE PROCEDURE customer_buy_sets(
	branchId INT,
    email VARCHAR(50),
    quantity INT,
    sname VARCHAR(100)
)
BEGIN
	DECLARE setId INT DEFAULT -1;
    DECLARE setPrice DECIMAL(6,2);
    DECLARE setNum INT;
    DECLARE balanceLeft DECIMAL(6,2);
    DECLARE setNotFound TINYINT DEFAULT FALSE;
    DECLARE setNumFlag TINYINT DEFAULT FALSE;
    DECLARE balanceLeftFlag TINYINT DEFAULT FALSE;
    DECLARE branchProfit DECIMAL(9,2);
    DECLARE setTotalPrice DECIMAL(6,2);
    DECLARE sqlError TINYINT DEFAULT FALSE;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
		SET sqlError = TRUE;
    START TRANSACTION;
    SELECT sid, price, numLeft INTO setId, setPrice, setNum FROM sets WHERE name = sname FOR SHARE; 
    SELECT balance INTO balanceLeft FROM customer WHERE customerEmail = email FOR SHARE;
    SELECT profit INTO branchProfit FROM branches WHERE cid = branchId FOR SHARE;
    SELECT set_total_price(setPrice, quantity) INTO setTotalPrice;
    IF setId = -1 THEN
		SET setNotFound = TRUE;
        SELECT 'No sets found!';
        ROLLBACK;
	END IF;
    IF quantity > setNum THEN
		SET setNumFlag = TRUE;
        SELECT 'Not enough sets left!';
        ROLLBACK;
	END IF;
    IF setTotalPrice > balanceLeft THEN
		SET balanceLeftFlag = TRUE;
		SELECT 'Need to charge first!';
        ROLLBACK;
	END IF;
    IF setNumFlag = FALSE AND balanceLeftFlag = FALSE AND setNotFound = FALSE THEN
		INSERT INTO sets_order VALUES(branchId, email, NOW(), quantity, setId);
        UPDATE sets SET numLeft = setNum - quantity WHERE sid = setId;
        UPDATE branches SET profit = branchProfit + setTotalPrice WHERE cid = branchId;
        UPDATE customer SET balance = balanceLeft - setTotalPrice WHERE customerEmail = email;
        SELECT 'Buy Success!';
	END IF;
    IF sqlError = TRUE THEN
		SELECT 'Error occurs! Transaction fails!';
		ROLLBACK;
	ELSE
		COMMIT;
	END IF;
END $$

DELIMITER $$
CREATE FUNCTION part_total_price(
	partPrice DECIMAL(6,2),
    quantity INT
)
RETURNS DECIMAL(6,2)
DETERMINISTIC NO SQL
BEGIN
	RETURN partPrice * quantity;
END $$

DELIMITER $$
CREATE PROCEDURE customer_buy_parts(
	branchId INT,
    email VARCHAR(50),
    quantity INT,
    pname VARCHAR(100)
)
BEGIN
	DECLARE partId INT DEFAULT -1;
    DECLARE partPrice DECIMAL(6,2);
    DECLARE partNum INT;
    DECLARE balanceLeft DECIMAL(6,2);
    DECLARE partNotFound TINYINT DEFAULT FALSE;
    DECLARE partNumFlag TINYINT DEFAULT FALSE;
    DECLARE balanceLeftFlag TINYINT DEFAULT FALSE;
    DECLARE branchProfit DECIMAL(9,2);
    DECLARE partTotalPrice DECIMAL(6,2);
    DECLARE sqlError TINYINT DEFAULT FALSE;
    DECLARE CONTINUE HANDLER FOR SQLEXCEPTION
		SET sqlError = TRUE;
    START TRANSACTION;
    SELECT pid, price, numLeft INTO partId, partPrice, partNum FROM parts WHERE name = pname FOR SHARE; 
    SELECT balance INTO balanceLeft FROM customer WHERE customerEmail = email FOR SHARE;
    SELECT profit INTO branchProfit FROM branches WHERE cid = branchId FOR SHARE;
    SELECT part_total_price(partPrice, quantity) INTO partTotalPrice;
	IF partId = -1 THEN
		SET partNotFound = TRUE;
        SELECT 'No parts found!';
        ROLLBACK;
	END IF;
    IF quantity > partNum THEN
		SET partNumFlag = TRUE;
        SELECT 'Not enough sets left!';
        ROLLBACK;
	END IF;
    IF partTotalPrice > balanceLeft THEN
		SET balanceLeftFlag = TRUE;
		SELECT 'Need to charge first!';
        ROLLBACK;
	END IF;
    IF partNumFlag = FALSE AND balanceLeftFlag = FALSE THEN
		INSERT INTO parts_order VALUES(branchId, email, NOW(), quantity, partId);
        UPDATE parts SET numLeft = partNum - quantity WHERE pid = partId;
        UPDATE branches SET profit = branchProfit + partTotalPrice WHERE cid = branchId;
        UPDATE customer SET balance = balanceLeft - partTotalPrice WHERE customerEmail = email;
        SELECT 'Buy Success!';
	END IF;
    IF sqlError = TRUE THEN
		SELECT 'Error occurs! Transaction fails!';
		ROLLBACK;
	ELSE
		COMMIT;
	END IF;
END $$

DELIMITER $$
CREATE PROCEDURE update_customer_info(
	email VARCHAR(50),
	updated_field VARCHAR(50),
    updated_value VARCHAR(50)
)
BEGIN
	IF updated_field = 'name' THEN
		UPDATE customer SET customerName = updated_value WHERE customerEmail = email;
        SELECT 'Update customer name success!';
	ELSEIF updated_field = 'address' THEN
		UPDATE customer SET zipCode = updated_value WHERE customerEmail = email;
        SELECT 'Update customer address success!';
    END IF;
END $$

DELIMITER $$
CREATE PROCEDURE customer_charge(
	email VARCHAR(50),
    updated_value VARCHAR(50)
)
BEGIN
	DECLARE remain_balance DECIMAL(6,2);
	SELECT balance INTO remain_balance FROM customer WHERE customerEmail = email;
	UPDATE customer SET balance = remain_balance + updated_value WHERE customerEmail = email;
	SELECT 'Charge success!';
END $$

DELIMITER $$
CREATE PROCEDURE customer_unsubscribe(
	email VARCHAR(50)
)
BEGIN
	DELETE FROM customer WHERE customerEmail = email;
    SELECT 'Unsubscribe Success!';
END $$

DELIMITER $$
CREATE PROCEDURE find_all_sets()
BEGIN
	SELECT * FROM sets WHERE numLeft > 0;
END $$

DELIMITER $$
CREATE PROCEDURE find_sets_by_name(
	sets_name VARCHAR(50)
)
BEGIN
	SELECT * FROM sets WHERE name LIKE CONCAT('%', sets_name, '%') AND numLeft > 0;
END $$

DELIMITER $$
CREATE PROCEDURE find_sets_by_release(
	lower_release INT,
    upper_release INT
)
BEGIN
	SELECT * FROM sets WHERE numLeft > 0 AND releaseYear BETWEEN lower_release AND upper_release;
END $$

DELIMITER $$
CREATE PROCEDURE find_sets_by_part_num(
	lower_part_num INT,
    upper_part_num INT
)
BEGIN
	SELECT * FROM sets WHERE numLeft > 0 AND partNum BETWEEN lower_part_num AND upper_part_num;
END $$

DELIMITER $$
CREATE PROCEDURE find_sets_by_price(
	lower_price DECIMAL(6,2),
    upper_price DECIMAL(6,2)
)
BEGIN
	SELECT * FROM sets WHERE numLeft > 0 AND price BETWEEN lower_price AND upper_price;
END $$

DELIMITER $$
CREATE PROCEDURE find_sets_by_theme(
	theme_name VARCHAR(50)
)
BEGIN
	SELECT * FROM sets s JOIN themes t 
		ON s.tid = t.tid 
	WHERE s.numLeft > 0 AND t.name = theme_name;
END $$

DELIMITER $$
CREATE PROCEDURE find_sets_by_conditions(
	sets_name VARCHAR(50),
    lower_release INT,
    upper_release INT,
    lower_part_num INT,
    upper_part_num INT,
    lower_price DECIMAL(6,2),
    upper_price DECIMAL(6,2),
    theme_name VARCHAR(50)
)
BEGIN
	DECLARE sets_query VARCHAR(200);
	SET sets_query = "SELECT * FROM sets s JOIN themes t WHERE s.numLeft > 0";
	IF sets_name <> '' THEN
		SET sets_query = CONCAT(sets_query, " AND s.name LIKE '%", sets_name, "%'");
	END IF;
    IF lower_release <> 0 OR upper_release <> 0 THEN
		IF lower_release <> 0 AND upper_release <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND releaseYear BETWEEN ", lower_release, " AND ", upper_release);
		ELSEIF lower_release <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND releaseYear >= ", lower_release);
		ELSEIF upper_release <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND releaseYear <= ", upper_release);
		END IF;
	END IF;
    IF lower_part_num <> 0 OR upper_part_num <> 0 THEN
		IF lower_part_num <> 0 AND upper_part_num <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND partNum BETWEEN ", lower_part_num, " AND ", upper_part_num);
		ELSEIF lower_part_num <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND partNum >= ", lower_part_num);
		ELSEIF upper_part_num <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND partNum <= ", upper_part_num);
		END IF;
	END IF;
    IF lower_price <> 0 OR upper_price <> 0 THEN
		IF lower_price <> 0 AND upper_price <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND price BETWEEN ", lower_price, " AND ", upper_price);
		ELSEIF lower_price <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND price >= ", lower_price);
		ELSEIF upper_price <> 0 THEN
			SET sets_query = CONCAT(sets_query, " AND price <= ", upper_price);
		END IF;
	END IF;
    IF theme_name <> '' THEN
		SET sets_query = CONCAT(sets_query, " AND t.name = '", theme_name, "'");
	END IF;
	SET @sets_query_by_conditions := sets_query;
	PREPARE sets_query_statement FROM @sets_query_by_conditions;
    EXECUTE sets_query_statement;
    DEALLOCATE PREPARE sets_query_statement;
END $$

DELIMITER $$
CREATE PROCEDURE find_all_parts()
BEGIN
	SELECT * FROM parts WHERE numLeft > 0;
END $$

DELIMITER $$
CREATE PROCEDURE find_parts_by_name(
	parts_name VARCHAR(50)
)
BEGIN
	SELECT * FROM parts WHERE name LIKE CONCAT('%', parts_name, '%') AND numLeft > 0;
END $$

DELIMITER $$
CREATE PROCEDURE find_parts_by_price(
	lower_price DECIMAL(6,2),
    upper_price DECIMAL(6,2)
)
BEGIN
	SELECT * FROM parts WHERE numLeft > 0 AND price BETWEEN lower_price AND upper_price;
END $$

DELIMITER $$
CREATE PROCEDURE find_parts_by_color(
	color_name VARCHAR(50)
)
BEGIN
	SELECT * FROM parts p JOIN color c 
		ON p.cname = c.name
	WHERE p.numLeft > 0 AND c.name = color_name;
END $$

DELIMITER $$
CREATE PROCEDURE find_parts_by_category(
	category_name VARCHAR(50)
)
BEGIN
	SELECT * FROM parts p JOIN category cat
		ON p.catId = cat.pid
	WHERE p.numLeft > 0 AND cat.name = category_name;
END $$

DELIMITER $$
CREATE PROCEDURE find_parts_by_conditions(
	parts_name VARCHAR(50),
    lower_price DECIMAL(6,2),
    upper_price DECIMAL(6,2),
    color_name VARCHAR(50),
    category_name VARCHAR(50)
)
BEGIN
	DECLARE parts_query VARCHAR(200);
	SET parts_query = "SELECT * FROM parts p JOIN color c ON p.cname = c.name JOIN categories cat ON p.catId = cat.catId WHERE p.numLeft > 0";
	IF parts_name <> '' THEN
		SET parts_query = CONCAT(parts_query, " AND p.name LIKE '%", parts_name, "%'");
	END IF;
    IF lower_price <> 0 OR upper_price <> 0 THEN
		IF lower_price <> 0 AND upper_price <> 0 THEN
			SET parts_query = CONCAT(parts_query, " AND price BETWEEN ", lower_price, " AND ", upper_price);
		ELSEIF lower_price <> 0 THEN
			SET parts_query = CONCAT(parts_query, " AND price >= ", lower_price);
		ELSEIF upper_price <> 0 THEN
			SET parts_query = CONCAT(parts_query, " AND price <= ", upper_price);
		END IF;
	END IF;
    IF color_name <> '' THEN
		SET parts_query = CONCAT(parts_query, " AND p.cname = '", color_name, "'");
	END IF;
    IF category_name <> '' THEN
		SET parts_query = CONCAT(parts_query, " AND cat.name = '", category_name, "'");
	END IF;
	SET @parts_query_by_conditions := parts_query;
	PREPARE parts_query_statement FROM @parts_query_by_conditions;
    EXECUTE parts_query_statement;
    DEALLOCATE PREPARE parts_query_statement;
END $$

DELIMITER $$
CREATE PROCEDURE staff_login(
	username VARCHAR(100),
    password VARCHAR(100)
)
BEGIN
	SELECT * FROM staff WHERE staffName = username AND staffPassword = password;
END $$

DELIMITER $$
CREATE PROCEDURE find_sets_by_left()
BEGIN
	SELECT * FROM sets WHERE numLeft < 20;
END $$

DELIMITER $$
CREATE PROCEDURE find_parts_by_left()
BEGIN
	SELECT * FROM parts WHERE numLeft < 20;
END $$

DELIMITER $$
CREATE FUNCTION find_branch_by_staff_id(
	id VARCHAR(50)
)
RETURNS INT
DETERMINISTIC READS SQL DATA
BEGIN
	DECLARE branchId INT;
    SELECT s.cid INTO branchId FROM staff s JOIN branches b 
		ON s.cid = b.cid 
	WHERE staffId = id;
    RETURN (branchId);
END $$

DELIMITER $$
CREATE FUNCTION find_sets_by_exact_name(
	setName VARCHAR(100)
)
RETURNS INT
DETERMINISTIC READS SQL DATA
BEGIN
	DECLARE setId INT DEFAULT -1;
	SELECT sid INTO setId FROM sets WHERE name = setName;
    RETURN (setId);
END $$

DELIMITER $$
CREATE FUNCTION find_parts_by_exact_name(
	partName VARCHAR(100)
)
RETURNS INT
DETERMINISTIC READS SQL DATA
BEGIN
	DECLARE partId INT DEFAULT -1;
	SELECT pid INTO partId FROM parts WHERE name = partName;
    RETURN (partId);
END $$

DELIMITER $$
CREATE FUNCTION get_restock_sets_id(
	id INT
)
RETURNS INT
DETERMINISTIC CONTAINS SQL
BEGIN
	DECLARE ssid INT DEFAULT -1;
    DECLARE business_time DATETIME;
    SELECT CURDATE() INTO business_time;
    SELECT restockId INTO ssid FROM set_restock WHERE sDate = business_time AND staffId = id;
    IF ssid = -1 THEN
		INSERT INTO set_restock(sDate,staffId) VALUES (business_time, id);
		SELECT restockId INTO ssid FROM set_restock WHERE sDate = business_time AND staffId = id;
    END IF;
    RETURN (ssid);
END $$

DELIMITER $$
CREATE FUNCTION get_restock_parts_id(
	id INT
)
RETURNS INT
DETERMINISTIC CONTAINS SQL
BEGIN
	DECLARE ssid INT DEFAULT -1;
    DECLARE business_time DATETIME;
    SELECT CURDATE() INTO business_time;
    SELECT restockId INTO ssid FROM part_restock WHERE rDate = business_time AND staffId = id;
    IF ssid = -1 THEN
		INSERT INTO part_restock(rDate,staffId) VALUES (business_time, id);
		SELECT restockId INTO ssid FROM part_restock WHERE rDate = business_time AND staffId = id;
    END IF;
    RETURN (ssid);
END $$

DELIMITER $$
CREATE PROCEDURE get_restock_sets_details(
	rid INT,
	setId INT,
    setName VARCHAR(100),
    quantity INT,
    releaseYear YEAR,
    partNum INT,
    price DECIMAL(6,2),
    themeName VARCHAR(50)
)
BEGIN
	DECLARE themeId INT;
	IF setId <> -1 THEN
		INSERT INTO set_restock_detail VALUES(rid, setId, quantity);
        SELECT 'Restock sets success!';
	ELSE
        SELECT find_theme_by_name(themeName) INTO themeId;
        IF themeId <> -1 THEN
			INSERT INTO sets(name, releaseYear, partNum, numLeft, price, tid) 
				VALUES (setName, releaseYear, partNum, 0, price, themeId);
            SELECT sid INTO setId FROM sets WHERE name = setName;
            INSERT INTO set_restock_detail VALUES(rid, setId, quantity);
            SELECT 'Restock sets success!';
		ELSE
			SELECT 'No theme found!';
		END IF;
	END IF;
END $$

DELIMITER $$
CREATE PROCEDURE get_restock_parts_details(
	rid INT,
	partId INT,
    partName VARCHAR(100),
    quantity INT,
    price DECIMAL(6,2),
    colorName VARCHAR(50),
    categoryName VARCHAR(50)
)
BEGIN
	DECLARE catId INT;
    DECLARE colorId INT;
	IF partId <> -1 THEN
		INSERT INTO part_restock_detail VALUES(rid, partId, quantity);
        SELECT 'Restock parts success!';
	ELSE
        SELECT find_category_by_name(categoryName) INTO catId;
        SELECT find_color_by_name(colorName) INTO colorId;
        IF catId <> -1 AND colorId <> -1 THEN
			INSERT INTO parts(name, numLeft, price, cname, catId) 
				VALUES (partName, 0, price, colorName, catId);
            SELECT pid INTO partId FROM parts WHERE name = partName;
            INSERT INTO part_restock_detail VALUES(rid, partId, quantity);
            SELECT 'Restock parts success!';
		ELSEIF catId = -1 THEN
			SELECT 'No category found!';
		ELSEIF colorId = -1 THEN
			SELECT 'No color found!';
        END IF;
	END IF;
END $$

DELIMITER $$
CREATE FUNCTION find_theme_by_name(
	themeName VARCHAR(100)
)
RETURNS INT
DETERMINISTIC READS SQL DATA
BEGIN
	DECLARE themeId INT DEFAULT -1;
	SELECT tid INTO themeId FROM themes WHERE name = themeName;
    RETURN (themeId);
END $$

DELIMITER $$
CREATE FUNCTION find_category_by_name(
	categoryName VARCHAR(100)
)
RETURNS INT
DETERMINISTIC READS SQL DATA
BEGIN
	DECLARE cid INT DEFAULT -1;
	SELECT catId INTO cid FROM categories WHERE name = categoryName;
    RETURN (cid);
END $$

DELIMITER $$
CREATE FUNCTION find_color_by_name(
	colorName VARCHAR(100)
)
RETURNS INT
DETERMINISTIC READS SQL DATA
BEGIN
	DECLARE cname VARCHAR(50) DEFAULT '';
	SELECT name INTO cname FROM color WHERE name = colorName;
    IF cname = '' THEN
		RETURN -1;
	ELSE
		RETURN 1;
	END IF;
END $$

DELIMITER $$
CREATE TRIGGER sets_increment
	AFTER INSERT ON set_restock_detail
    FOR EACH ROW
BEGIN
	UPDATE sets SET numLeft = numLeft + NEW.quatity WHERE sid = NEW.sid;
END $$

DROP TRIGGER sets_increment;

DELIMITER $$
CREATE TRIGGER parts_increment
	AFTER INSERT ON part_restock_detail
    FOR EACH ROW
BEGIN
	UPDATE parts SET numLeft = numLeft + NEW.quatity WHERE pid = NEW.pid;
END $$

DROP TRIGGER parts_increment;

DELIMITER $$
CREATE EVENT monthly_delete_set_restock
ON SCHEDULE EVERY 1 MONTH
STARTS '2022-12-01'
DO BEGIN
	DELETE FROM set_restock WHERE sDate < NOW() - INTERVAL 1 MONTH;
END $$

DELIMITER $$
CREATE EVENT monthly_delete_part_restock
ON SCHEDULE EVERY 1 MONTH
STARTS '2022-12-01'
DO BEGIN
	DELETE FROM part_restock WHERE rDate < NOW() - INTERVAL 1 MONTH;
END $$
