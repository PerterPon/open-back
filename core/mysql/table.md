这个文件记录的是所有表结构：

CREATE TABLE `kline` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `gmt_create` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `gmt_modify` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `currency` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time_interval` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time` timestamp NULL DEFAULT NULL,
  `o` double DEFAULT NULL,
  `h` double DEFAULT NULL,
  `l` double DEFAULT NULL,
  `c` double DEFAULT NULL,
  `v` double DEFAULT NULL,
  `extra` text COLLATE utf8mb4_unicode_ci,
  `comment` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_currency` (`currency`),
  KEY `idx_interval` (`time_interval`),
  KEY `idx_time` (`time`),
  KEY `idx_currency_interval` (`currency`,`time_interval`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `real_mock_record` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `gmt_create` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `gmt_modify` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `strategy_id` int DEFAULT NULL,
  `is_delete` int DEFAULT NULL,
  `comment` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE `strategy` (
  `id` int unsigned NOT NULL AUTO_INCREMENT,
  `gmt_create` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `gmt_modify` timestamp NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `name` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `currency` varchar(32) COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `time_interval` varchar(16) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci DEFAULT NULL,
  `sharpe_ratio` double DEFAULT NULL,
  `trade_count` int DEFAULT NULL,
  `trades` text COLLATE utf8mb4_unicode_ci,
  `total_commission` double DEFAULT NULL,
  `max_drawdown` double DEFAULT NULL,
  `winning_percentage` double DEFAULT NULL,
  `reason` text CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci,
  `init_balance` double DEFAULT NULL,
  `final_balance` double DEFAULT NULL,
  `extra` text COLLATE utf8mb4_unicode_ci,
  PRIMARY KEY (`id`),
  KEY `idx_sharp_ratio` (`sharpe_ratio`),
  KEY `idx_final_balance` (`final_balance`),
  KEY `idx_max_drawdown` (`max_drawdown`),
  KEY `idx_trade_count` (`trade_count`),
  KEY `idx_total_commission` (`total_commission`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

