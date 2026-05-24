
-- ---------------------------------------------------------------------------
-- EXTENSIONES
-- ---------------------------------------------------------------------------
CREATE EXTENSION IF NOT EXISTS unaccent;

-- =============================================================================
-- NIVEL 0: CATÁLOGOS CONTROLADOS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- cat_tipos_contenido
-- Discriminador principal: Movie / TV Show
-- ---------------------------------------------------------------------------
CREATE TABLE cat_tipos_contenido (
    id_tipo         SERIAL          PRIMARY KEY,
    nombre_tipo     VARCHAR(20)     NOT NULL UNIQUE,  -- 'Movie', 'TV Show'
    descripcion     TEXT
);

COMMENT ON TABLE  cat_tipos_contenido               IS 'Tipos de contenido admitidos en la plataforma.';
COMMENT ON COLUMN cat_tipos_contenido.nombre_tipo   IS 'Valor canónico del campo type del CSV original.';

-- ---------------------------------------------------------------------------
-- cat_clasificaciones
-- Rating de audiencia (PG-13, TV-MA, etc.)
-- ---------------------------------------------------------------------------
CREATE TABLE cat_clasificaciones (
    id_clasificacion    SERIAL          PRIMARY KEY,
    codigo              VARCHAR(10)     NOT NULL UNIQUE,  -- 'PG-13', 'TV-MA' …
    descripcion         VARCHAR(120)
);

COMMENT ON TABLE  cat_clasificaciones           IS 'Clasificaciones de audiencia (MPAA / TV Parental Guidelines).';
COMMENT ON COLUMN cat_clasificaciones.codigo    IS 'Código oficial del sistema de clasificación.';

-- ---------------------------------------------------------------------------
-- cat_paises
-- Catálogo ISO de países para descomponer el campo multi-valor "country"
-- ---------------------------------------------------------------------------
CREATE TABLE cat_paises (
    id_pais     SERIAL          PRIMARY KEY,
    nombre      VARCHAR(100)    NOT NULL UNIQUE
);

COMMENT ON TABLE cat_paises IS 'Catálogo de países de producción.';

-- ---------------------------------------------------------------------------
-- cat_generos
-- Cada entrada de listed_in se descompone en géneros individuales
-- ---------------------------------------------------------------------------
CREATE TABLE cat_generos (
    id_genero   SERIAL          PRIMARY KEY,
    nombre      VARCHAR(100)    NOT NULL UNIQUE  -- 'Documentaries', 'TV Dramas' …
);

COMMENT ON TABLE cat_generos IS 'Géneros/categorías de contenido normalizados desde listed_in.';

-- =============================================================================
-- NIVEL 1: ENTIDADES MAESTRAS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- personas
-- Unifica directores y actores bajo una sola entidad (patron "Party")
-- Evita duplicar atributos nombre/apellido en dos tablas separadas.
-- ---------------------------------------------------------------------------
CREATE TABLE personas (
    id_persona  SERIAL          PRIMARY KEY,
    nombre_completo VARCHAR(200) NOT NULL UNIQUE
);

COMMENT ON TABLE  personas               IS 'Directores y actores como entidad unificada (patrón Party).';
COMMENT ON COLUMN personas.nombre_completo IS 'Nombre tal como aparece en el CSV, limpio de espacios.';

-- =============================================================================
-- NIVEL 2: ENTIDADES TRANSACCIONALES — TÍTULOS
-- =============================================================================

-- ---------------------------------------------------------------------------
-- titulos
-- Entidad central. Sólo atributos atómicos y de dependencia directa a la PK.
-- Los campos multi-valor (cast, country, listed_in) se normalizan en Nivel 3.
-- ---------------------------------------------------------------------------
CREATE TABLE titulos (
    id_titulo           SERIAL          PRIMARY KEY,
    show_id             VARCHAR(20)     NOT NULL UNIQUE,    -- clave natural del CSV ('s1', 's2'…)
    id_tipo             INT             NOT NULL REFERENCES cat_tipos_contenido(id_tipo)  ON UPDATE CASCADE,
    id_clasificacion    INT             REFERENCES cat_clasificaciones(id_clasificacion) ON UPDATE CASCADE,
    titulo              VARCHAR(300)    NOT NULL,
    fecha_agregado      DATE,                               -- date_added parseado
    anio_estreno        SMALLINT        NOT NULL CHECK (anio_estreno BETWEEN 1888 AND 2100),
    -- Duración normalizada: separamos valor numérico y unidad
    duracion_valor      SMALLINT        CHECK (duracion_valor > 0),  -- 90, 2, 1 …
    duracion_unidad     VARCHAR(15)     CHECK (duracion_unidad IN ('min', 'Season', 'Seasons')),
    descripcion         TEXT,
    created_at          TIMESTAMPTZ     NOT NULL DEFAULT NOW()
);

COMMENT ON TABLE  titulos               IS 'Catálogo central de títulos de la plataforma Netflix.';
COMMENT ON COLUMN titulos.show_id       IS 'Identificador natural proveniente del CSV original (show_id).';
COMMENT ON COLUMN titulos.duracion_valor IS 'Parte numérica de la duración (90 para "90 min", 2 para "2 Seasons").';
COMMENT ON COLUMN titulos.duracion_unidad IS 'Unidad de duración: min | Season | Seasons.';

CREATE INDEX idx_titulos_tipo            ON titulos(id_tipo);
CREATE INDEX idx_titulos_clasificacion   ON titulos(id_clasificacion);
CREATE INDEX idx_titulos_anio            ON titulos(anio_estreno);

-- =============================================================================
-- NIVEL 3: TABLAS DE ASOCIACIÓN N:M
-- =============================================================================

-- ---------------------------------------------------------------------------
-- titulo_directores   (titulo N:M persona)
-- Un título puede tener varios directores; un director puede dirigir varios.
-- ---------------------------------------------------------------------------
CREATE TABLE titulo_directores (
    id_titulo   INT NOT NULL REFERENCES titulos(id_titulo)   ON DELETE CASCADE ON UPDATE CASCADE,
    id_persona  INT NOT NULL REFERENCES personas(id_persona)  ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (id_titulo, id_persona)
);

COMMENT ON TABLE titulo_directores IS 'Relación N:M entre títulos y sus directores.';

-- ---------------------------------------------------------------------------
-- titulo_actores   (titulo N:M persona)
-- Un título tiene muchos actores; un actor aparece en muchos títulos.
-- ---------------------------------------------------------------------------
CREATE TABLE titulo_actores (
    id_titulo   INT NOT NULL REFERENCES titulos(id_titulo)   ON DELETE CASCADE ON UPDATE CASCADE,
    id_persona  INT NOT NULL REFERENCES personas(id_persona)  ON DELETE CASCADE ON UPDATE CASCADE,
    orden_credito SMALLINT,   -- posición en el reparto (1 = primer crédito)
    PRIMARY KEY (id_titulo, id_persona)
);

COMMENT ON TABLE  titulo_actores             IS 'Relación N:M entre títulos y su reparto.';
COMMENT ON COLUMN titulo_actores.orden_credito IS 'Orden de aparición en los créditos del CSV original.';

CREATE INDEX idx_titulo_actores_persona ON titulo_actores(id_persona);

-- ---------------------------------------------------------------------------
-- titulo_paises   (titulo N:M pais)
-- Un título puede ser coproducción de varios países.
-- ---------------------------------------------------------------------------
CREATE TABLE titulo_paises (
    id_titulo   INT NOT NULL REFERENCES titulos(id_titulo)   ON DELETE CASCADE ON UPDATE CASCADE,
    id_pais     INT NOT NULL REFERENCES cat_paises(id_pais)   ON DELETE CASCADE ON UPDATE CASCADE,
    es_primario BOOLEAN NOT NULL DEFAULT FALSE,  -- TRUE si es el primer país listado
    PRIMARY KEY (id_titulo, id_pais)
);

COMMENT ON TABLE  titulo_paises             IS 'Relación N:M entre títulos y países de producción.';
COMMENT ON COLUMN titulo_paises.es_primario IS 'Indica si es el país principal (primera entrada en el campo country original).';

-- ---------------------------------------------------------------------------
-- titulo_generos   (titulo N:M genero)
-- Un título pertenece a múltiples géneros.
-- ---------------------------------------------------------------------------
CREATE TABLE titulo_generos (
    id_titulo   INT NOT NULL REFERENCES titulos(id_titulo)   ON DELETE CASCADE ON UPDATE CASCADE,
    id_genero   INT NOT NULL REFERENCES cat_generos(id_genero) ON DELETE CASCADE ON UPDATE CASCADE,
    PRIMARY KEY (id_titulo, id_genero)
);

COMMENT ON TABLE titulo_generos IS 'Relación N:M entre títulos y géneros/categorías.';

-- =============================================================================
-- VISTAS DE CONVENIENCIA (recrean la fila plana original para consultas BI)
-- =============================================================================

CREATE OR REPLACE VIEW v_titulos_planos AS
SELECT
    t.show_id,
    tc.nombre_tipo                                              AS type,
    t.titulo                                                    AS title,
    STRING_AGG(DISTINCT pd.nombre_completo, ', ' ORDER BY pd.nombre_completo) AS director,
    STRING_AGG(DISTINCT pa.nombre_completo, ', ' ORDER BY pa.nombre_completo) AS cast,
    STRING_AGG(DISTINCT cp.nombre, ', ' ORDER BY cp.nombre)    AS country,
    t.fecha_agregado,
    t.anio_estreno                                              AS release_year,
    cl.codigo                                                   AS rating,
    CASE
        WHEN t.duracion_unidad = 'min'
            THEN t.duracion_valor::TEXT || ' min'
        ELSE t.duracion_valor::TEXT || ' ' || t.duracion_unidad
    END                                                         AS duration,
    STRING_AGG(DISTINCT g.nombre, ', ' ORDER BY g.nombre)      AS listed_in,
    t.descripcion                                               AS description
FROM titulos t
JOIN cat_tipos_contenido  tc ON tc.id_tipo           = t.id_tipo
LEFT JOIN cat_clasificaciones cl ON cl.id_clasificacion = t.id_clasificacion
LEFT JOIN titulo_directores   td ON td.id_titulo      = t.id_titulo
LEFT JOIN personas            pd ON pd.id_persona     = td.id_persona
LEFT JOIN titulo_actores      ta ON ta.id_titulo      = t.id_titulo
LEFT JOIN personas            pa ON pa.id_persona     = ta.id_persona
LEFT JOIN titulo_paises       tp ON tp.id_titulo      = t.id_titulo
LEFT JOIN cat_paises          cp ON cp.id_pais        = tp.id_pais
LEFT JOIN titulo_generos      tg ON tg.id_titulo      = t.id_titulo
LEFT JOIN cat_generos          g ON g.id_genero       = tg.id_genero
GROUP BY t.id_titulo, tc.nombre_tipo, cl.codigo;

COMMENT ON VIEW v_titulos_planos IS 'Vista desnormalizada que reconstruye la fila original del CSV para consumo analítico.';