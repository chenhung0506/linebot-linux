CREATE DATABASE IF NOT EXISTS `emotibot` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE `xeon_kg`;
START TRANSACTION;

CREATE DATABASE IF NOT EXISTS `emotibot` DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;

    drop table if exists emotibot.property;
    create table emotibot.property(
        pro_id INT NOT NULL AUTO_INCREMENT,
        serial VARCHAR(20) NOT NULL,
        name VARCHAR(80) NOT NULL,
        quantity VARCHAR(3),
        vendor VARCHAR(10),
        buy_date VARCHAR(12),
        keeper VARCHAR(20),
        keeper_date VARCHAR(12),
        product_serial VARCHAR(80),
        PRIMARY KEY ( pro_id )
    )engine=InnoDB default charset=utf8mb4 collate utf8mb4_general_ci comment='竹間產品清單';
    
   
   select * from emotibot.property p
   
   
   


select name,sum(quantity) 
from emotibot.property 
where name like 'Macbook%'
or name like '%PC%'
or name like '%螢幕%'
or name like '%主機%'
or name like '%平板%'
or name like '%話機%'
or name like '%行動硬碟%'
or name like '%AP%'
or name like '%電筆%'
or name like '%webcam%'
or name like '%NAS%'
or name like '%Pad%'
or name like '%攝影機%'
or name like '%WiFi%'
or name like '%交換器%'
or name like '%電視%'
or name like '%電腦%'
or name like '%UPS%'
or name like '%Freeswitch%'
or name like '%Switch%'
or name like '%TV%' 
group by name
order by name


COMMIT;
