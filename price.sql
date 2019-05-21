/* drop tables */
DROP TABLE IF EXISTS `price`;

/* create tables */
CREATE TABLE `price` (
  `article` varchar(500) NOT NULL,
  `kod` varchar(255) NOT NULL,
  `name` text NOT NULL,
  `cena` decimal(10,2) NOT NULL,
  `valuta` varchar(10) NOT NULL,
  `nalichie` varchar(255) NOT NULL,
  `postavchik` varchar(255) NOT NULL,
  `data_dobavleniya` date NOT NULL,
  `img` varchar(500) NOT NULL
);
