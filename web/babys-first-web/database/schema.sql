create table users (
   `id` INT AUTO_INCREMENT,
   `username` VARCHAR(100) NOT NULL,
   `password` VARCHAR(40) NOT NULL,
   PRIMARY KEY ( `id` )
);

INSERT INTO users (`username`,`password`) VALUES ('admin', '1234');