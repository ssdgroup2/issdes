#
# SQL Export
# Created by Querious (302003)
# Created: 13 April 2022 12:29:49 CEST
# Encoding: Unicode (UTF-8)
#


SET @ORIG_FOREIGN_KEY_CHECKS = @@FOREIGN_KEY_CHECKS;
SET FOREIGN_KEY_CHECKS = 0;

SET @ORIG_UNIQUE_CHECKS = @@UNIQUE_CHECKS;
SET UNIQUE_CHECKS = 0;

SET @ORIG_TIME_ZONE = @@TIME_ZONE;
SET TIME_ZONE = '+00:00';

SET @ORIG_SQL_MODE = @@SQL_MODE;
SET SQL_MODE = 'NO_AUTO_VALUE_ON_ZERO';



DROP DATABASE IF EXISTS `issdes`;
CREATE DATABASE `issdes` DEFAULT CHARACTER SET utf8mb4 DEFAULT COLLATE utf8mb4_0900_ai_ci;
USE `issdes`;




DROP TABLE IF EXISTS `userauthns`;
DROP TABLE IF EXISTS `storedfiles`;
DROP TABLE IF EXISTS `datauser`;
DROP TABLE IF EXISTS `datagroups`;


CREATE TABLE `datagroups` (
  `groupid` varchar(2) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'two digit group number 00 - 99',
  `groupname` varchar(45) CHARACTER SET utf8 COLLATE utf8_general_ci NOT NULL COMMENT 'ISSDES group names',
  `groupdesc` varchar(90) CHARACTER SET utf8 COLLATE utf8_general_ci DEFAULT NULL COMMENT 'Data classification and group functions',
  `grouptype` int NOT NULL COMMENT 'corresponding integer values of group functions,  EG 1 = standard/open,  2 = commercial, 3 = agency proprietary  etc.',
  PRIMARY KEY (`groupid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


CREATE TABLE `datauser` (
  `userid` int NOT NULL AUTO_INCREMENT COMMENT 'auto incrementing digits,  obscured from user because they pass accessid on login page.',
  `userforename` varchar(45) NOT NULL,
  `usersurname` varchar(45) NOT NULL,
  `userdisplayname` varchar(90) NOT NULL COMMENT 'Minimum 1 character,  max 90',
  `useraccessid` varchar(12) NOT NULL COMMENT ' character agency / company code followed by up to 5 digits and 1 random letters   abcd87e497   ~ 250,000 possible usernames  Unique constraint should handle any name space collisions)',
  `useragency` varchar(45) DEFAULT NULL COMMENT 'Name of space agency user is associated with.  User can only belong to on space agency. Potential for normalization in the future releases, agency management was out of scope',
  `authgroups` varchar(60) DEFAULT NULL COMMENT 'Can contain zero to 20 2 digit numbers that represent groups the user could belong to. This provides a possible 99 unique groups.  Seperate each group identifier with a comma simplify the function retrieving membership. ',
  PRIMARY KEY (`userid`),
  UNIQUE KEY `useraccessid_UNIQUE` (`useraccessid`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb3;


CREATE TABLE `storedfiles` (
  `uuid_hex` varchar(32) NOT NULL,
  `filename` varchar(128) NOT NULL COMMENT 'Maximum file name size if 128 characters including extention and dot seperator',
  `filetype` varchar(8) NOT NULL COMMENT 'This should normally be 3 or 4,  things .tar.gz may be observed but we should actually reject anything with more than one extension as suspicious  8 seems like all we''d every need at this point ',
  `filedata` longblob NOT NULL COMMENT 'Long blob provides up to 4 gigabyte of storage but this app also processes only in memory so we need to cap the files at 32 or 64 meg for now.  both exeed the next largest blob size, 16 meg.  If performance were really an issue this could be dropped to a medium blob if 16 meg is an acceptable limit.  This seems less likely in a science data situation, large files are not uncommon.',
  `fileowner` int NOT NULL COMMENT 'File owner value is int,  this will suppport thousands of users over time, can be assured to be unique with the database.  ',
  `authgroups` varchar(60) DEFAULT NULL COMMENT 'Allows up to 20 groups to be granted access to a specific file. This can be null since the owner can always be granted access to their files but they may not share them with anyone.\nData content will be 2 digit numbers, comma seperated, no spaces.  This can be brought in from the object to the authorization code as a list.  ',
  `filecreate` datetime NOT NULL COMMENT 'This will be automatically generated on upload and used for inital insert. This becomes a non-repudiation control when combined with the owner ID which is also automatically retrieved from the logged in user. \n( New versions of the file will have a new date, which can be used to track versions.) The core issue with this is duplicate file names but if we include file size and date they could tell them apart.  ',
  `filesize` int NOT NULL COMMENT 'Store this as a value in the class so we can request this as part of getfilemetadata() instead of calculating it off the raw bytes.  This will be useful for presenting since it will be a consistent response time.',
  `keywords_tags` varchar(255) DEFAULT NULL COMMENT 'Use 255 for max keywords & tags.  Can be null.  ',
  `allowupdates` tinyint DEFAULT '0' COMMENT 'By default files are not updateable, option should be for versioning instead since scientific  data should be tracked at all phases of the research. Also enables redundency at the process level.\n',
  `fileversion` int NOT NULL DEFAULT '1' COMMENT 'New files, or versions of the file can have the same name but the version number will be increased. ',
  PRIMARY KEY (`uuid_hex`),
  KEY `userid_idx` (`fileowner`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;


CREATE TABLE `userauthns` (
  `id` int NOT NULL COMMENT 'Each new user account created will have a unique ID but this is a foreign key from the auto-incremented data user table. Therefore reuse of account names, access ID''s etc will always reflect the most current user.  Auto-increment also ensures no account ID could accidently be reused (authorization for file access is based on group membership but file ownership is tied to userid) \nNote,  this must be called ID in order to work with Flask, due to a hardcoded setting in Flask-login manager\n',
  `userpasswd` varchar(102) NOT NULL COMMENT 'Using WerkZeug security built in function for generating for storing ',
  `userlocked` tinyint NOT NULL DEFAULT '0' COMMENT 'Boolean value that can be set is suspicous activity is detected for a given account, allows quick protection and subsequent unlocking without forcing a password change\n',
  `forcepwdchange` tinyint NOT NULL DEFAULT '0' COMMENT 'Place holder for future implementation phase\n',
  `activestatus` tinyint NOT NULL DEFAULT '1' COMMENT 'User information may need to be retained for the puposes of maintaining file ownership ortransaction history. Inactive accounts provide a possible application compromise path, checking enabled/disabled can be implemented programatically even before testing passwords, reducing the feasibilty of attacks like password spraying or credential stuffing\n',
  `passwdchange` datetime DEFAULT NULL COMMENT 'Placeholder for future enhancement to enforce periodic password rotation',
  `userregistration` datetime NOT NULL COMMENT 'Date user account was created, forcing as a required field to support non-repudiation and security incident investigation requirements',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb3;




LOCK TABLES `datagroups` WRITE;
INSERT INTO `datagroups` (`groupid`, `groupname`, `groupdesc`, `grouptype`) VALUES 
	('03','NA_Standard','North America Joint Research Open Group',1),
	('04','EU_Standard','European & International Joint Research Open Group',1),
	('05','EU_Commercial','EU Commercial',1),
	('06','US_Commercial','United States Commercial',1),
	('08','AP_Standard','Asia Pacific Joint Research Open Group',1),
	('09','JP_Commercial','Japan Commercial',2),
	('11','US_Restricted','United States Space Agency Members Only',3),
	('12','RU_Restricted','Russian Space Agency Members Only',3),
	('14','EU_Restricted','EU Space Agency Members Only',3),
	('15','JP_Restricted','Japan Space Agency Members Only',3),
	('18','INT_Standard','International Open Research',1),
	('19','CA_Restricted','Canadian Space Agency Members Only',3),
	('60','EU_Climate','EU Climate Researches',1);
UNLOCK TABLES;


LOCK TABLES `datauser` WRITE;
INSERT INTO `datauser` (`userid`, `userforename`, `usersurname`, `userdisplayname`, `useraccessid`, `useragency`, `authgroups`) VALUES 
	(1,'Gurkan','Huray','Gurkan Huray','EU999G99n','Europe','19');
UNLOCK TABLES;


LOCK TABLES `storedfiles` WRITE;
UNLOCK TABLES;


LOCK TABLES `userauthns` WRITE;
INSERT INTO `userauthns` (`id`, `userpasswd`, `userlocked`, `forcepwdchange`, `activestatus`, `passwdchange`, `userregistration`) VALUES 
	(1,'pbkdf2:sha256:260000$yOrdsR2iLO47Mm19$aec704c7e33d306e179f5ef9117134e6fd5e39b9e9a476d02ba1961e4c0a8a22',0,0,1,NULL,'2022-04-12 22:28:25');
UNLOCK TABLES;






SET FOREIGN_KEY_CHECKS = @ORIG_FOREIGN_KEY_CHECKS;

SET UNIQUE_CHECKS = @ORIG_UNIQUE_CHECKS;

SET @ORIG_TIME_ZONE = @@TIME_ZONE;
SET TIME_ZONE = @ORIG_TIME_ZONE;

SET SQL_MODE = @ORIG_SQL_MODE;



# Export Finished: 13 April 2022 12:29:49 CEST

