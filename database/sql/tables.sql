CREATE TABLE IF NOT EXISTS categorias(
    id SERIAL PRIMARY KEY,
    categoria TEXT
);

--DELETE FROM categorias;
--INSERT INTO categorias(categoria) VALUES('MATES');
--INSERT INTO categorias(categoria) VALUES('LLAVEROS');
--INSERT INTO categorias(categoria) VALUES('IDENTIFICADORES');
--INSERT INTO categorias(categoria) VALUES('OTROS');
--INSERT INTO categorias(categoria) VALUES('COMPUTACION');


CREATE TABLE IF NOT EXISTS productos(
    id SERIAL PRIMARY KEY,
    descripcion TEXT,
    idCategoria INTEGER,
    fechaCreacion DATE,
    estado BOOL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS piezas(
    id SERIAL PRIMARY KEY,
    descripcion TEXT NOT NULL,
    peso INTEGER NOT NULL,
    horas INTEGER NOT NULL,
    minutos INTEGER NOT NULL,
    idProducto INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS extras(
    id SERIAL PRIMARY KEY,
    descripcion TEXT NOT NULL,
    precio FLOAT NOT NULL
);



--DELETE FROM extras;
--INSERT INTO extras(descripcion,precio) VALUES('POLIMERO NOST3RD', 59);
--INSERT INTO extras(descripcion,precio) VALUES('BOMBILLA ALUMINIO CON LIMPIADOR', 50);

CREATE TABLE IF NOT EXISTS extra_producto(
    idProducto INTEGER NOT NULL,
    idExtra INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios(
    id SERIAL PRIMARY KEY,
    usuario TEXT NOT NULL,
    password TEXT NOT NULL
);

--INSERT INTO usuarios (usuario, password) VALUES('fmartinez','pbkdf2:sha256:260000$b5ILhWjDCVRrpIIm$90afca4c99f2c17f34feb7ab48bca800a95ecad6ffc0c16c52b26abd32f04190');
--INSERT INTO usuarios (usuario, password) VALUES('lvidela','pbkdf2:sha256:260000$b5ILhWjDCVRrpIIm$90afca4c99f2c17f34feb7ab48bca800a95ecad6ffc0c16c52b26abd32f04190');