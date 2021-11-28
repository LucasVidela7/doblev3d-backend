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

CREATE TABLE IF NOT EXISTS precio_unitario(
    id SERIAL PRIMARY KEY,
    idproducto INTEGER NOT NULL,
    precioUnitario FLOAT NOT NULL,
    ganancia FLOAT,
    costoTotal FLOAT,
    fechaActualizacion DATE
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

CREATE TABLE IF NOT EXISTS ventas(
    id SERIAL PRIMARY KEY,
    cliente TEXT NOT NULL,
    contacto TEXT,
    fechaCreacion DATE,
    idestado INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas_productos(
    id SERIAL PRIMARY KEY,
    idventa INTEGER NOT NULL,
    idproducto INTEGER NOT NULL,
    costototal FLOAT,
    ganancia FLOAT,
    descuento INTEGER DEFAULT 0,
    preciounidad FLOAT,
    adddata TEXT,
    observaciones TEXT,
    idestado INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS ventas_productos_piezas(
    id SERIAL PRIMARY KEY,
    iddetalle INTEGER NOT NULL,
    idpieza INTEGER NOT NULL,
    idestado INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS pagos(
    id SERIAL PRIMARY KEY,
    monto FLOAT NOT NULL,
    idventa INTEGER NOT NULL,
    fechaPago DATE,
    idMedioPago INTEGER
);

CREATE TABLE IF NOT EXISTS medios_pago(
    id SERIAL PRIMARY KEY,
    descripcion TEXT
);

CREATE TABLE IF NOT EXISTS estados(
    id SERIAL PRIMARY KEY,
    estado TEXT,
    ventas BIT,
    productos BIT,
    piezas BIT,
    saltear BIT,
    icono TEXT
);





