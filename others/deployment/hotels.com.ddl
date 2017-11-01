create schema hotelamenities;
use hotelamenities;
CREATE TABLE `amenities` (
  `Id` int(11) NOT NULL,
  `hotelid` int(11) NOT NULL,
  `amenityid` int(11) NOT NULL,
  `isfree` int(11) NOT NULL,
  `description` varchar(128) NOT NULL,
  `displayorder` int(11) NOT NULL DEFAULT '1',
  `label` varchar(32) DEFAULT NULL,
  PRIMARY KEY (`Id`),
  KEY `hotelid` (`hotelid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE `generalamenities` (
  `Id` int(11) NOT NULL,
  `category` varchar(128) NOT NULL,
  `amenity` varchar(128) NOT NULL,
  `icon` varchar(256) DEFAULT NULL,
  PRIMARY KEY (`Id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE `searchqueueamenities` (
  `sessionid` varchar(512) NOT NULL,
  `hotelid` int(11) NOT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `hotelid` (`hotelid`),
  CONSTRAINT `hotelidfk2` FOREIGN KEY (`hotelid`) REFERENCES `amenities` (`hotelid`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=9040 DEFAULT CHARSET=utf8;
create schema hoteldeals;
use hoteldeals;
CREATE TABLE `deals` (
  `id` int(11) NOT NULL,
  `agency` varchar(256) DEFAULT NULL,
  `hotelid` int(11) DEFAULT NULL,
  `roomtype` varchar(128) DEFAULT NULL,
  `fromdt` date DEFAULT NULL,
  `todt` date DEFAULT NULL,
  `price` int(11) DEFAULT NULL,
  `active` tinyint(4) DEFAULT NULL,
  PRIMARY KEY (`id`),
  KEY `hotelid` (`hotelid`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
CREATE TABLE `searchqueuedeals` (
  `sessionid` varchar(512) NOT NULL,
  `hotelid` int(11) NOT NULL,
  `time` datetime DEFAULT CURRENT_TIMESTAMP,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  KEY `hotelid` (`hotelid`),
  CONSTRAINT `hotelidfk1` FOREIGN KEY (`hotelid`) REFERENCES `deals` (`hotelid`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=8973 DEFAULT CHARSET=utf8;

INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('1', 'Hotel facilities', '24-hour room service');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('2', 'Hotel facilities', '24-hour reception');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('3', 'Hotel facilities', 'Airport shuttle');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('4', 'Hotel facilities', 'Beach / sun umbrellas');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('5', 'Hotel facilities', 'Business centre');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('6', 'Hotel facilities', 'Car park');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('7', 'Hotel facilities', 'Concierge');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('8', 'Hotel facilities', 'Conference rooms');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('9', 'Hotel facilities', 'Deck chairs / Sun loungers');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('10', 'Hotel facilities', 'Express check-in / out');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`, `icon`) VALUES ('11', 'Hotel facilities', 'WiFi in lobby', 'images/icons/wifi.svg');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`, `icon`) VALUES ('12', 'Hotel facilities', 'Gym', 'images/icons/gym.svg');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('13', 'Hotel facilities', 'Hotel bar');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('14', 'Hotel facilities', 'Hotel safe');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('15', 'Hotel facilities', 'Laundry service');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('16', 'Hotel facilities', 'Lift');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('17', 'Hotel facilities', 'Nightclub');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('18', 'Hotel facilities', 'Non-smoking rooms');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`, `icon`) VALUES ('19', 'Hotel facilities', 'Outdoor swimming pool', 'images/icons/pool.svg');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('20', 'Hotel facilities', 'PC with internet');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('21', 'Hotel facilities', 'Pets allowed');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('22', 'Hotel facilities', 'Porter service');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('23', 'Hotel facilities', 'Restaurant');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('24', 'Hotel facilities', 'Room service');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('25', 'Hotel facilities', 'Terrace');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`) VALUES ('26', 'Hotel facilities', 'Washing machine');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`, `icon`) VALUES ('27', 'Hotel facilities', 'Wellness Centre / Spa', 'images/icons/spa.svg');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`, `icon`) VALUES ('28', 'Hotel facilities', 'WiFi in Rooms', 'images/icons/wifi.svg');
INSERT INTO `hotelamenities`.`generalamenities` (`Id`, `category`, `amenity`, `icon`) VALUES ('29', 'Room facilities', 'Air conditioning', 'images/icons/ac.svg');

