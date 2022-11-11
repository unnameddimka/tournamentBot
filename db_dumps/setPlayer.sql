
DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `setPlayer`(IN telegram_id VARCHAR(45),IN str_name VARCHAR(45),IN str_country VARCHAR(45),IN str_rank VARCHAR(45))
BEGIN 
	
	

		INSERT INTO player (`id`,`name`,`country`,`rank`) 
        VALUES 
			(telegram_id,str_name,str_country,str_rank)
		ON DUPLICATE KEY UPDATE
			`name` = str_name, `country` = str_country, `rank` = str_rank;
        
   
END$$
DELIMITER ;
