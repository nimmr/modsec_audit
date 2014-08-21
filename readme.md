

Requirements
============

* python 2.6 minimum
* python-mysqldb
* OrderedDict: pip install ordereddict

DB Tables
=========

```
CREATE TABLE `modsec_site` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `site` varchar(255) NOT NULL,
  `added` datetime NOT NULL,
  `last_run_date` datetime NOT NULL,
  `last_parsed_date` datetime DEFAULT NULL,
  `total_count` bigint(20) unsigned NOT NULL,
  PRIMARY KEY (`id`),
  KEY `site` (`site`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `modsec_ip` (
  `id` int(11) unsigned NOT NULL AUTO_INCREMENT,
  `ip` varchar(15) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `modsec_runstatus` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `run_date` datetime NOT NULL,
  `status` varchar(45) NOT NULL,
  `parsed` int(11) DEFAULT NULL,
  `parse_errors` int(11) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;

CREATE TABLE `modsec_parse_error` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `runstatus_id` int(10) unsigned DEFAULT NULL,
  `file` varchar(100) DEFAULT NULL,
  `message` varchar(500) DEFAULT NULL,
  `contents` blob,
  PRIMARY KEY (`id`),
  KEY `error_runstatus_id_idx` (`runstatus_id`),
  CONSTRAINT `error_runstatus_id` FOREIGN KEY (`runstatus_id`) REFERENCES `modsec_runstatus` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

CREATE TABLE `modsec_hit` (
  `uniq` varchar(24) CHARACTER SET latin1 NOT NULL,
  `site_id` int(10) unsigned NOT NULL,
  `ip_id` int(11) unsigned NOT NULL,
  `datetime` datetime NOT NULL,
  `modsec_id` mediumint(8) unsigned NOT NULL,
  `contents` blob,
  PRIMARY KEY (`uniq`),
  KEY `date` (`datetime`),
  KEY `id` (`modsec_id`),
  KEY `ip` (`ip_id`),
  KEY `fk_site_site_id_idx` (`site_id`),
  CONSTRAINT `fk_site_ip_id` FOREIGN KEY (`ip_id`) REFERENCES `modsec_ip` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `fk_site_site_id` FOREIGN KEY (`site_id`) REFERENCES `modsec_site` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
```