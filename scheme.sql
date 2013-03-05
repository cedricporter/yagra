DROP TABLE IF EXISTS `yagra_image`;
DROP TABLE IF EXISTS `yagra_user`;

-- 用户表
CREATE TABLE `yagra_user` (
  `ID` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_login` varchar(60) NOT NULL DEFAULT '',
  `user_passwd` varchar(64) NOT NULL DEFAULT '',
  `user_email` varchar(100) NOT NULL DEFAULT '',
  `user_register` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  `user_status` int(11) NOT NULL DEFAULT '0',
  `display_name` varchar(256) NOT NULL DEFAULT '',
  PRIMARY KEY (`ID`),
  KEY `user_login_key` (`user_login`),
  KEY `user_email_key` (`user_email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 图片表
CREATE TABLE `yagra_image` (
  `image_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `filename` varchar(256) NOT NULL,
  `upload_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`image_id`),
  KEY `user_id_ind` (`user_id`),
  CONSTRAINT `yagra_image_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `yagra_user` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;

-- 添加用户
GRANT select, update, insert ON yagra.* to `yagra`@`localhost` IDENTIFIED BY 'yagra_p@$$w0rd';
FLUSH PRIVILEGES;
