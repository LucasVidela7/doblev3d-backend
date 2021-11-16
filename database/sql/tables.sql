CREATE TABLE IF NOT EXISTS categorias(
    id SERIAL PRIMARY KEY,
    categoria TEXT
);


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

CREATE TABLE IF NOT EXISTS extra_producto(
    idProducto INTEGER NOT NULL,
    idExtra INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS extra_categorias(
    idCategoria INTEGER NOT NULL,
    idExtra INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios(
    id SERIAL PRIMARY KEY,
    usuario TEXT NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS cotizacion(
    key TEXT NOT NULL,
    value FLOAT NOT NULL
);