CREATE SCHEMA IF NOT EXISTS `takestock1.0`;
# Use the Set as Default Schema (from right-click on name) to set pointer to this database
DROP Table players;
CREATE TABLE `players` (
  `username` varchar(200) NOT NULL,
  `password` varchar(500) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL,
  `role` varchar(20) NULL DEFAULT " ",
  `email` varchar(100) DEFAULT NULL,
  `player_number` int NULL DEFAULT 0,
  `cash_on_hand` decimal(10,2) NULL DEFAULT 0,
  `property_value` decimal(10,2) NULL DEFAULT 0,
  `stock_value` decimal(10,2) NULL DEFAULT 0,
  `commodity_value` decimal(10,2) NULL DEFAULT 0,
  `other_investments` decimal(10,2) NULL DEFAULT 0,
  `status` varchar(20) NULL DEFAULT " ",
  `job_level` int NULL DEFAULT 0,
  `degree_level` int NULL DEFAULT 0,
  `game_ID` varchar(20) NOT NULL,
  `salary` decimal(10,2) NULL DEFAULT 0, 
  `city_addr` varchar(20) NULL DEFAULT " ",
  `time` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
DROP TABLE game;
CREATE TABLE `game` (
	`username` varchar(200) NOT NULL,
    `game_ID` varchar(20) NOT NULL,
    `player_count` int DEFAULT 0,
    `start_date` DATE DEFAULT(CURRENT_DATE),
    `status` varchar(20) NOT NULL,
    `move_count` bigint DEFAULT 0,
    `gdp` decimal(14,2) DEFAULT 0,
    `gs_gdp` decimal(14,2) DEFAULT 0,
    `population` bigint DEFAULT 0,
    `pop_chg` decimal(10,2) DEFAULT 0,
    `game_level` varchar(20) NOT NULL DEFAULT " ",
    `game_goal` varchar(20) NOT NULL DEFAULT " ",
    `total_spending` decimal(14,2) DEFAULT 0,
    `total_earnings` decimal(14,2) DEFAULT 0,
    primary key (`game_ID`)
);
INSERT INTO game (username,game_ID,start_date,status)
VALUES ("wallytauriac", "TS2024-07-14", "2024-07-14", "New");
Drop Table investments;
CREATE TABLE `investments` (
	`invest_id` int NOT NULL AUTO_INCREMENT,
	`invest_type` varchar(20) NOT NULL,
    `invest_count` int DEFAULT NULL, 
    `invest_value` decimal(14,2),
    `invest_description` varchar(30) NOT NULL,
    `player_number` int DEFAULT NULL,
    PRIMARY KEY (`invest_id`)
);
INSERT INTO players (username, password, name, role, email)
VALUES ("wallyj", "Evenodd!512", "Wally J", "Host", "wallytauriac@example.com");
Drop table address;
CREATE TABLE `address` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Address` varchar(20) DEFAULT NULL,
  `District` varchar(50) DEFAULT NULL,
  `Property` varchar(100) DEFAULT NULL,
  `BLDG_type` varchar(50) DEFAULT NULL,
  `PPTY_type` varchar(50) DEFAULT NULL,
  `Price`  decimal(14,2) DEFAULT 0,
  `mkt_value`  decimal(14,2) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=47 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
Drop Table business;
CREATE TABLE `business` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Street` varchar(20) DEFAULT NULL,
  `business` varchar(100) DEFAULT NULL,
  `buy` decimal(10,0) DEFAULT 0,
  `partner` decimal(10,0) DEFAULT 0,
  `club` decimal(12,0) DEFAULT 0,
  `value` decimal(14,0) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=30 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
Drop Table commodities;
CREATE TABLE `commodities` (
  `id` int NOT NULL AUTO_INCREMENT,
  `Mutual` decimal(10,0) DEFAULT NULL,
  `Diamonds` decimal(10,0) DEFAULT NULL,
  `Grain` decimal(10,0) DEFAULT NULL,
  `Security` decimal(10,0) DEFAULT NULL,
  `Silver` decimal(10,0) DEFAULT NULL,
  `Certificates` decimal(10,3) DEFAULT 0,
  `Money` decimal(10,3) DEFAULT 0,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
Drop Table jobcenter;
CREATE TABLE `jobcenter` (
  `code` char(5) DEFAULT "JC",
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(10) DEFAULT NULL,
  `short_description` varchar(100) DEFAULT NULL,
  `long_description` varchar(500) DEFAULT NULL,
  `amount` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
Drop Table learncenter;
CREATE TABLE `learncenter` (
  `code` char(5) DEFAULT "LC",
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(10) DEFAULT NULL,
  `short_description` varchar(100) DEFAULT NULL,
  `long_description` varchar(500) DEFAULT NULL,
  `amount` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
Drop Table lifecenter;
CREATE TABLE `lifecenter` (
  `code` char(5) DEFAULT "LC2",
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(10) DEFAULT NULL,
  `short_description` varchar(100) DEFAULT NULL,
  `long_description` varchar(500) DEFAULT NULL,
  `amount` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
Drop Table stockcenter;
CREATE TABLE `stockcenter` (
  `code` char(5) DEFAULT "SC",
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(10) DEFAULT NULL,
  `short_description` varchar(100) DEFAULT NULL,
  `long_description` varchar(500) DEFAULT NULL,
  `count` decimal(10,0) DEFAULT NULL,
  `amount` decimal(12,0) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
Drop Table stocks;
CREATE TABLE `stocks` (
  `id` int NOT NULL AUTO_INCREMENT,
  `oNg` decimal(10,0) DEFAULT NULL,
  `robotics` decimal(10,0) DEFAULT NULL,
  `gold` decimal(10,0) DEFAULT NULL,
  `paper` decimal(10,0) DEFAULT NULL,
  `utility` decimal(10,0) DEFAULT NULL,
  `auto` decimal(10,0) DEFAULT NULL,
  `airline` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=51 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
Drop Table opportunities;
Create TABLE `opportunities` (
  `code` char(5) DEFAULT "OPP",
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(10) DEFAULT NULL,
  `OWN_code` char(5) DEFAULT " ",
  `short_description` varchar(100) DEFAULT NULL,
  `long_description` varchar(500) DEFAULT NULL,
  `INVITES`  varchar(30) DEFAULT " ",
  `amount` decimal(12,0) DEFAULT NULL,
  `count` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`id`)
);
Drop Table shopping;
Create TABLE `shopping` (
  `code` char(5) DEFAULT "OPP",
  `id` int NOT NULL AUTO_INCREMENT,
  `type` varchar(10) DEFAULT NULL,
  `short_description` varchar(100) DEFAULT NULL,
  `long_description` varchar(200) DEFAULT NULL,
  `INVITES`  varchar(10) DEFAULT NULL,
  `amount` decimal(12,0) DEFAULT NULL,
  `count` decimal(10,0) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

