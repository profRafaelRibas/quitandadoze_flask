CREATE TABLE IF NOT EXISTS produtos (
    id_prod INTEGER PRIMARY KEY,
    nome_prod TEXT NOT NULL,
    desc_prod TEXT NOT NULL,
    preco REAL NOT NULL,
    img TEXT NOT NULL
);