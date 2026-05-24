-- =============================================================================
-- DML DE PRUEBA PARA NETFLIX
-- Inserciones en orden respetando claves foráneas
-- =============================================================================

-- =============================================================================
-- 1. CATÁLOGOS (NIVEL 0)
-- =============================================================================

-- cat_tipos_contenido
INSERT INTO cat_tipos_contenido (nombre_tipo, descripcion) VALUES
('Movie', 'Película de duración fija'),
('TV Show', 'Serie de televisión con temporadas');

-- cat_clasificaciones
INSERT INTO cat_clasificaciones (codigo, descripcion) VALUES
('G', 'Apto para todas las edades'),
('PG', 'Guía parental sugerida'),
('PG-13', 'Puede ser inapropiado para menores de 13'),
('R', 'Restringido, menores de 17 requieren acompañante'),
('TV-14', 'No apto para menores de 14'),
('TV-MA', 'Para audiencias maduras'),
('NR', 'No clasificado');

-- cat_paises
INSERT INTO cat_paises (nombre) VALUES
('Estados Unidos'), ('Reino Unido'), ('Canadá'), ('Francia'), ('Alemania'),
('España'), ('México'), ('Argentina'), ('Japón'), ('Corea del Sur');

-- cat_generos
INSERT INTO cat_generos (nombre) VALUES
('Acción'), ('Aventura'), ('Animación'), ('Comedia'), ('Crimen'),
('Documental'), ('Drama'), ('Familiar'), ('Fantasía'), ('Historia'),
('Misterio'), ('Romance'), ('Ciencia ficción'), ('Suspenso'), ('Terror');

-- =============================================================================
-- 2. PERSONAS (NIVEL 1)
-- =============================================================================

INSERT INTO personas (nombre_completo) VALUES
('Christopher Nolan'),
('David Fincher'),
('Greta Gerwig'),
('Quentin Tarantino'),
('Ava DuVernay'),
('Leonardo DiCaprio'),
('Brad Pitt'),
('Meryl Streep'),
('Robert Downey Jr.'),
('Scarlett Johansson');

-- =============================================================================
-- 3. TÍTULOS (NIVEL 2)
-- =============================================================================

INSERT INTO titulos (show_id, id_tipo, id_clasificacion, titulo, fecha_agregado, anio_estreno, duracion_valor, duracion_unidad, descripcion) VALUES
('s1', (SELECT id_tipo FROM cat_tipos_contenido WHERE nombre_tipo = 'Movie'), (SELECT id_clasificacion FROM cat_clasificaciones WHERE codigo = 'PG-13'), 'Inception', '2020-01-15', 2010, 148, 'min', 'Un ladrón que roba secretos del subconsciente debe plantar una idea en la mente de un CEO.'),
('s2', (SELECT id_tipo FROM cat_tipos_contenido WHERE nombre_tipo = 'Movie'), (SELECT id_clasificacion FROM cat_clasificaciones WHERE codigo = 'R'), 'Fight Club', '2019-11-10', 1999, 139, 'min', 'Un oficinista insomne y un fabricante de jabón forman un club de lucha clandestino.'),
('s3', (SELECT id_tipo FROM cat_tipos_contenido WHERE nombre_tipo = 'TV Show'), (SELECT id_clasificacion FROM cat_clasificaciones WHERE codigo = 'TV-MA'), 'Stranger Things', '2020-07-01', 2016, 4, 'Seasons', 'Un grupo de niños descubre fenómenos sobrenaturales en su pequeño pueblo.'),
('s4', (SELECT id_tipo FROM cat_tipos_contenido WHERE nombre_tipo = 'Movie'), (SELECT id_clasificacion FROM cat_clasificaciones WHERE codigo = 'PG-13'), 'The Social Network', '2021-03-20', 2010, 120, 'min', 'La historia de la fundación de Facebook y las disputas legales posteriores.'),
('s5', (SELECT id_tipo FROM cat_tipos_contenido WHERE nombre_tipo = 'TV Show'), (SELECT id_clasificacion FROM cat_clasificaciones WHERE codigo = 'TV-14'), 'The Crown', '2020-11-17', 2016, 5, 'Seasons', 'Biografía de la reina Isabel II y los eventos que definieron su reinado.');

-- =============================================================================
-- 4. ASOCIACIONES N:M (NIVEL 3)
-- =============================================================================

-- titulo_directores
INSERT INTO titulo_directores (id_titulo, id_persona)
SELECT t.id_titulo, p.id_persona
FROM titulos t, personas p
WHERE (t.show_id = 's1' AND p.nombre_completo = 'Christopher Nolan')
   OR (t.show_id = 's2' AND p.nombre_completo = 'David Fincher')
   OR (t.show_id = 's3' AND p.nombre_completo = 'Christopher Nolan')  -- ejemplo: Nolan dirigió episodios de Stranger Things? No realmente, solo para prueba
   OR (t.show_id = 's4' AND p.nombre_completo = 'David Fincher')
   OR (t.show_id = 's5' AND p.nombre_completo = 'Greta Gerwig');  -- no es real, pero de muestra

-- titulo_actores
INSERT INTO titulo_actores (id_titulo, id_persona, orden_credito)
VALUES
((SELECT id_titulo FROM titulos WHERE show_id = 's1'), (SELECT id_persona FROM personas WHERE nombre_completo = 'Leonardo DiCaprio'), 1),
((SELECT id_titulo FROM titulos WHERE show_id = 's1'), (SELECT id_persona FROM personas WHERE nombre_completo = 'Brad Pitt'), 2),
((SELECT id_titulo FROM titulos WHERE show_id = 's2'), (SELECT id_persona FROM personas WHERE nombre_completo = 'Brad Pitt'), 1),
((SELECT id_titulo FROM titulos WHERE show_id = 's3'), (SELECT id_persona FROM personas WHERE nombre_completo = 'Scarlett Johansson'), 1),
((SELECT id_titulo FROM titulos WHERE show_id = 's4'), (SELECT id_persona FROM personas WHERE nombre_completo = 'Meryl Streep'), 2);

-- titulo_paises
INSERT INTO titulo_paises (id_titulo, id_pais, es_primario)
VALUES
((SELECT id_titulo FROM titulos WHERE show_id = 's1'), (SELECT id_pais FROM cat_paises WHERE nombre = 'Estados Unidos'), TRUE),
((SELECT id_titulo FROM titulos WHERE show_id = 's1'), (SELECT id_pais FROM cat_paises WHERE nombre = 'Reino Unido'), FALSE),
((SELECT id_titulo FROM titulos WHERE show_id = 's2'), (SELECT id_pais FROM cat_paises WHERE nombre = 'Estados Unidos'), TRUE),
((SELECT id_titulo FROM titulos WHERE show_id = 's3'), (SELECT id_pais FROM cat_paises WHERE nombre = 'Estados Unidos'), TRUE),
((SELECT id_titulo FROM titulos WHERE show_id = 's4'), (SELECT id_pais FROM cat_paises WHERE nombre = 'Estados Unidos'), TRUE),
((SELECT id_titulo FROM titulos WHERE show_id = 's5'), (SELECT id_pais FROM cat_paises WHERE nombre = 'Reino Unido'), TRUE);

-- titulo_generos
INSERT INTO titulo_generos (id_titulo, id_genero)
SELECT t.id_titulo, g.id_genero
FROM titulos t, cat_generos g
WHERE (t.show_id = 's1' AND g.nombre IN ('Acción', 'Ciencia ficción', 'Suspenso'))
   OR (t.show_id = 's2' AND g.nombre IN ('Drama', 'Crimen'))
   OR (t.show_id = 's3' AND g.nombre IN ('Ciencia ficción', 'Misterio', 'Terror'))
   OR (t.show_id = 's4' AND g.nombre IN ('Drama', 'Historia'))
   OR (t.show_id = 's5' AND g.nombre IN ('Drama', 'Historia'));

-- =============================================================================
-- FIN DML DE PRUEBA
-- =============================================================================