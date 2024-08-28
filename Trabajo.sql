

USE Prototipo;

CREATE TABLE user(
idUser INT AUTO_INCREMENT,
nane VARCHAR(75) NOT NULL,
photo LONGBLOB,

CONSTRAINT pk_user_idUser PRIMARY KEY(idUser)
);

SELECT * FROM `user`;