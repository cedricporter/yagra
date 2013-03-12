-- Author: Hua Liang[Stupid ET]
--

CREATE DATABASE IF NOT EXISTS `yagra`;

DROP TABLE IF EXISTS `yagra`.`yagra_user_head`;
DROP TABLE IF EXISTS `yagra`.`yagra_image`;
DROP TABLE IF EXISTS `yagra`.`yagra_user`;
DROP TABLE IF EXISTS `yagra`.`yagra_session`;


-- 用户表
CREATE TABLE `yagra`.`yagra_user` (
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
CREATE TABLE `yagra`.`yagra_image` (
  `image_id` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `user_id` bigint(20) unsigned NOT NULL,
  `filename` varchar(256) NOT NULL,
  `upload_date` datetime NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`image_id`),
  KEY `user_id_ind` (`user_id`),
  CONSTRAINT `yagra_image_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `yagra_user` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- 主头像关联表
CREATE TABLE `yagra`.`yagra_user_head` (
  `image_id` bigint(20) unsigned NOT NULL,
  `user_id` bigint(20) unsigned NOT NULL,
  `user_email_md5` char(32) NOT NULL,
  PRIMARY KEY (`image_id`, `user_id`),
  KEY `user_email_md5_ind` (`user_email_md5`),
  CONSTRAINT `yagra_user_head_ibfk_1` FOREIGN KEY (`user_id`) REFERENCES `yagra_user` (`ID`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `yagra_user_head_ibfk_2` FOREIGN KEY (`image_id`) REFERENCES `yagra_image` (`image_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;


-- Session表
CREATE TABLE `yagra`.`yagra_session` (
  `session_id` char(64) NOT NULL,
  `atime` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `data` text,
  PRIMARY KEY (`session_id`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;


-- 添加用户
GRANT select, update, insert, delete ON yagra.* to `yagra`@`localhost` IDENTIFIED BY 'yagra_p@$$w0rd';
FLUSH PRIVILEGES;
