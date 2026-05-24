-- ============================================================================
-- 1. TABLAS DE CATÁLOGOS INDEPENDIENTES (Nivel 0)
-- ============================================================================

CREATE TABLE cat_especialidades (
    id_especialidad INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_especialidad VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE cat_aseguradoras (
    id_aseguradora INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_aseguradora VARCHAR(100) NOT NULL UNIQUE,
    telefono_contacto VARCHAR(20)
);

CREATE TABLE cat_habitaciones (
    id_habitacion INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    numero_habitacion VARCHAR(10) NOT NULL UNIQUE,
    tipo_habitacion VARCHAR(50) NOT NULL CHECK (tipo_habitacion IN ('General', 'UCI', 'Privada', 'Pediatría')),
    estado_habitacion VARCHAR(20) DEFAULT 'Disponible' CHECK (estado_habitacion IN ('Disponible', 'Ocupada', 'Mantenimiento'))
);

CREATE TABLE cat_medicamentos (
    id_medicamento INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre_comercial VARCHAR(150) NOT NULL,
    componente_actico VARCHAR(150) NOT NULL,
    presentacion VARCHAR(50) NOT NULL
);

-- ============================================================================
-- 2. TABLAS MAESTRAS / ENTIDADES PRINCIPALES (Nivel 1)
-- ============================================================================

CREATE TABLE medicos (
    id_medico INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    cedula_profesional VARCHAR(30) NOT NULL UNIQUE,
    id_especialidad INT NOT NULL,
    telefono VARCHAR(20),
    email VARCHAR(100) UNIQUE,
    CONSTRAINT fk_medico_especialidad FOREIGN KEY (id_especialidad) 
        REFERENCES cat_especialidades(id_especialidad) ON DELETE RESTRICT
);

CREATE TABLE pacientes (
    id_paciente INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    fecha_nacimiento DATE NOT NULL,
    genero CHAR(1) NOT NULL CHECK (genero IN ('M', 'F', 'O')),
    telefono VARCHAR(20),
    email VARCHAR(100),
    id_aseguradora INT,
    nss_seguro VARCHAR(30),
    CONSTRAINT fk_paciente_aseguradora FOREIGN KEY (id_aseguradora) 
        REFERENCES cat_aseguradoras(id_aseguradora) ON DELETE SET NULL
);

-- ============================================================================
-- 3. TABLAS TRANSACCIONALES / HECHOS (Nivel 2)
-- ============================================================================

CREATE TABLE citas_medicas (
    id_cita INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_paciente INT NOT NULL,
    id_medico INT NOT NULL,
    fecha_hora TIMESTAMP NOT NULL,
    motivo_consulta TEXT,
    estado_cita VARCHAR(20) DEFAULT 'Programada' CHECK (estado_cita IN ('Programada', 'Completada', 'Cancelada', 'No Asistió')),
    CONSTRAINT fk_cita_paciente FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente) ON DELETE CASCADE,
    CONSTRAINT fk_cita_medico FOREIGN KEY (id_medico) REFERENCES medicos(id_medico) ON DELETE RESTRICT
);

CREATE TABLE ingresos_hospitalarios (
    id_ingreso INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_paciente INT NOT NULL,
    id_habitacion INT NOT NULL,
    fecha_ingreso TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    fecha_alta TIMESTAMP,
    motivo_ingreso TEXT NOT NULL,
    CONSTRAINT fk_ingreso_paciente FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente) ON DELETE CASCADE,
    CONSTRAINT fk_ingreso_habitacion FOREIGN KEY (id_habitacion) REFERENCES cat_habitaciones(id_habitacion) ON DELETE RESTRICT
);

CREATE TABLE historiales_clinicos (
    id_historial INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_paciente INT NOT NULL,
    id_medico INT NOT NULL,
    fecha_registro TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    sintomas TEXT NOT NULL,
    diagnostico TEXT NOT NULL,
    CONSTRAINT fk_historial_paciente FOREIGN KEY (id_paciente) REFERENCES pacientes(id_paciente) ON DELETE CASCADE,
    CONSTRAINT fk_historial_medico FOREIGN KEY (id_medico) REFERENCES medicos(id_medico) ON DELETE RESTRICT
);

-- ============================================================================
-- 4. EVOLUCIÓN TRANSACCIONAL (Nivel 3)
-- ============================================================================

CREATE TABLE recetas_medicas (
    id_receta INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_historial INT NOT NULL UNIQUE, -- Relación estricta 1:1 con un diagnóstico específico
    fecha_emision DATE NOT NULL DEFAULT CURRENT_DATE,
    CONSTRAINT fk_receta_historial FOREIGN KEY (id_historial) REFERENCES historiales_clinicos(id_historial) ON DELETE CASCADE
);

CREATE TABLE detalles_recetas (
    id_detalle INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    id_receta INT NOT NULL,
    id_medicamento INT NOT NULL,
    dosis VARCHAR(100) NOT NULL,     -- Ej: '500 mg' o '1 tableta'
    frecuencia VARCHAR(100) NOT NULL, -- Ej: 'Cada 8 horas'
    duracion_dias INT NOT NULL CHECK (duracion_dias > 0),
    CONSTRAINT fk_detalle_receta FOREIGN KEY (id_receta) REFERENCES recetas_medicas(id_receta) ON DELETE CASCADE,
    CONSTRAINT fk_detalle_medicamento FOREIGN KEY (id_medicamento) REFERENCES cat_medicamentos(id_medicamento) ON DELETE RESTRICT
);

-- ============================================================================
-- 5. ÍNDICES DE RENDIMIENTO (Clave para JOINS masivos)
-- ============================================================================
CREATE INDEX idx_medicos_especialidad ON medicos(id_especialidad);
CREATE INDEX idx_pacientes_aseguradora ON pacientes(id_aseguradora);
CREATE INDEX idx_citas_paciente ON citas_medicas(id_paciente);
CREATE INDEX idx_citas_medico ON citas_medicas(id_medico);
CREATE INDEX idx_citas_fecha ON citas_medicas(fecha_hora);
CREATE INDEX idx_ingresos_paciente ON ingresos_hospitalarios(id_paciente);
CREATE INDEX idx_historiales_paciente ON historiales_clinicos(id_paciente);
CREATE INDEX idx_detalles_receta ON detalles_recetas(id_receta);