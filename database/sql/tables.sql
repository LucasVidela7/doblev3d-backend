CREATE TABLE IF NOT EXISTS categorias(
    id INTEGER PRIMARY KEY,
    categoria TEXT
);

DELETE FROM categorias;
INSERT INTO categorias(categoria) VALUES('MATES');
INSERT INTO categorias(categoria) VALUES('LLAVEROS');
INSERT INTO categorias(categoria) VALUES('IDENTIFICADORES');
INSERT INTO categorias(categoria) VALUES('OTROS');
INSERT INTO categorias(categoria) VALUES('COMPUTACION');


CREATE TABLE IF NOT EXISTS productos(
    id INTEGER PRIMARY KEY,
    descripcion TEXT,
    id_categoria INTEGER,
    fecha_creacion DATE,
    estado BIT DEFAULT 1,
    CONSTRAINT FK_categoria FOREIGN KEY (id_categoria) REFERENCES categorias(id)
);

CREATE TABLE IF NOT EXISTS piezas(
    id INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL,
    peso INTEGER NOT NULL,
    horas INTEGER NOT NULL,
    minutos INTEGER NOT NULL,
    id_producto INTEGER NOT NULL,
    CONSTRAINT FK_pieza_producto FOREIGN KEY (id_producto) REFERENCES productos(id)
);

CREATE TABLE IF NOT EXISTS extras(
    id INTEGER PRIMARY KEY,
    descripcion TEXT NOT NULL,
    precio FLOAT NOT NULL
);

CREATE TABLE IF NOT EXISTS extra_producto(
    id_producto INTEGER NOT NULL,
    id_extra INTEGER NOT NULL,
    CONSTRAINT FK_producto FOREIGN KEY (id_producto) REFERENCES productos(id)
    CONSTRAINT FK_extra FOREIGN KEY (id_extra) REFERENCES extras(id)
);