CREATE DATABASE IF NOT EXISTS `line` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `line`;
START TRANSACTION;

drop table if exists `line`.`contact_info`;
create table `line`.`contact_info`(
	id INT NOT NULL AUTO_INCREMENT,
    user VARCHAR(20) NOT NULL,
    init_date date,
    info VARCHAR(2048),
    PRIMARY KEY ( id )
)engine=InnoDB default charset=utf8mb4 collate utf8mb4_general_ci comment='留言訊息';

COMMIT;
