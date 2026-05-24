-- ============================================================
-- DML DE PRUEBA PARA ESQUEMA HOSPITALARIO
-- Inserción ordenada respetando claves foráneas
-- ============================================================

-- 1. CATÁLOGOS (Nivel 0)
-- ============================================================

-- Especialidades médicas
INSERT INTO cat_especialidades (nombre_especialidad) VALUES
('Medicina General'),
('Cardiología'),
('Neurología'),
('Neumología'),
('Pediatría'),
('Traumatología');

-- Aseguradoras
INSERT INTO cat_aseguradoras (nombre_aseguradora, telefono_contacto) VALUES
('Seguros Salud Total', '800-123-4567'),
('IMSS', '800-111-2222'),
('ISSSTE', '800-333-4444'),
('Particular', '555-000-1111'),
('Seguros Axa', '800-555-6666');

-- Habitaciones
INSERT INTO cat_habitaciones (numero_habitacion, tipo_habitacion, estado_habitacion) VALUES
('UCI-101', 'UCI', 'Ocupada'),
('UCI-102', 'UCI', 'Disponible'),
('UCI-103', 'UCI', 'Ocupada'),
('GEN-201', 'General', 'Disponible'),
('PED-301', 'Pediatría', 'Ocupada'),
('PRI-401', 'Privada', 'Mantenimiento');

-- Medicamentos
INSERT INTO cat_medicamentos (nombre_comercial, componente_actico, presentacion) VALUES
('Paracetamol', 'Paracetamol', 'Tabletas 500mg'),
('Ibuprofeno', 'Ibuprofeno', 'Cápsulas 400mg'),
('Omeprazol', 'Omeprazol', 'Cápsulas 20mg'),
('Amoxicilina', 'Amoxicilina', 'Suspensión 250mg/5ml'),
('Losartán', 'Losartán potásico', 'Tabletas 50mg'),
('Salbutamol', 'Salbutamol', 'Inhalador 100mcg/dosis');

-- 2. MAESTROS (Nivel 1)
-- ============================================================

-- Médicos (asociados a especialidades)
-- Nota: Se usan subconsultas para obtener id_especialidad por nombre
INSERT INTO medicos (nombre, apellido, cedula_profesional, id_especialidad, telefono, email) VALUES
('Laura', 'González', '1234567', (SELECT id_especialidad FROM cat_especialidades WHERE nombre_especialidad = 'Medicina General'), '555-100-2001', 'laura.gonzalez@hospital.com'),
('Carlos', 'Ramírez', '2345678', (SELECT id_especialidad FROM cat_especialidades WHERE nombre_especialidad = 'Cardiología'), '555-100-2002', 'carlos.ramirez@hospital.com'),
('Ana', 'Martínez', '3456789', (SELECT id_especialidad FROM cat_especialidades WHERE nombre_especialidad = 'Neurología'), '555-100-2003', 'ana.martinez@hospital.com'),
('Luis', 'Fernández', '4567890', (SELECT id_especialidad FROM cat_especialidades WHERE nombre_especialidad = 'Neumología'), '555-100-2004', 'luis.fernandez@hospital.com'),
('Marta', 'López', '5678901', (SELECT id_especialidad FROM cat_especialidades WHERE nombre_especialidad = 'Pediatría'), '555-100-2005', 'marta.lopez@hospital.com');

-- Pacientes (con o sin aseguradora)
INSERT INTO pacientes (nombre, apellido, fecha_nacimiento, genero, telefono, email, id_aseguradora, nss_seguro) VALUES
('Juan', 'Pérez', '1985-06-15', 'M', '555-200-1001', 'juan.perez@mail.com', (SELECT id_aseguradora FROM cat_aseguradoras WHERE nombre_aseguradora = 'Seguros Salud Total'), 'NSS-001'),
('María', 'López', '1992-09-23', 'F', '555-200-1002', 'maria.lopez@mail.com', (SELECT id_aseguradora FROM cat_aseguradoras WHERE nombre_aseguradora = 'IMSS'), 'NSS-002'),
('Pedro', 'García', '1978-12-10', 'M', '555-200-1003', 'pedro.garcia@mail.com', (SELECT id_aseguradora FROM cat_aseguradoras WHERE nombre_aseguradora = 'Particular'), NULL),
('Ana', 'Martínez', '2000-03-05', 'F', '555-200-1004', 'ana.martinez@mail.com', (SELECT id_aseguradora FROM cat_aseguradoras WHERE nombre_aseguradora = 'ISSSTE'), 'NSS-004'),
('Luis', 'Rodríguez', '1995-07-19', 'M', '555-200-1005', 'luis.rodriguez@mail.com', NULL, NULL),
('Sofía', 'Hernández', '1980-11-30', 'F', '555-200-1006', 'sofia.hernandez@mail.com', (SELECT id_aseguradora FROM cat_aseguradoras WHERE nombre_aseguradora = 'Seguros Axa'), 'NSS-006');

-- 3. TRANSACCIONALES (Nivel 2)
-- ============================================================

-- Citas médicas
INSERT INTO citas_medicas (id_paciente, id_medico, fecha_hora, motivo_consulta, estado_cita)
SELECT 
    p.id_paciente,
    m.id_medico,
    '2025-03-01 10:00:00'::timestamp + (random() * interval '60 days') as fecha_hora,
    CASE (random()*2)::int
        WHEN 0 THEN 'Dolor de cabeza'
        WHEN 1 THEN 'Chequeo general'
        ELSE 'Dificultad respiratoria'
    END,
    CASE (random()*3)::int
        WHEN 0 THEN 'Programada'
        WHEN 1 THEN 'Completada'
        WHEN 2 THEN 'Cancelada'
        ELSE 'No Asistió'
    END
FROM pacientes p
CROSS JOIN medicos m
WHERE p.id_paciente = 1 AND m.id_medico = 1  -- solo un par de ejemplo
UNION ALL
SELECT 2, 2, '2025-03-05 11:30:00', 'Dolor en pecho', 'Completada'
UNION ALL
SELECT 3, 3, '2025-03-10 09:00:00', 'Mareos', 'Programada'
UNION ALL
SELECT 4, 4, '2025-03-15 08:45:00', 'Tos persistente', 'Completada'
UNION ALL
SELECT 5, 5, '2025-03-20 12:00:00', 'Fiebre', 'Cancelada';

-- Ingresos hospitalarios
INSERT INTO ingresos_hospitalarios (id_paciente, id_habitacion, fecha_ingreso, fecha_alta, motivo_ingreso)
VALUES
(1, (SELECT id_habitacion FROM cat_habitaciones WHERE numero_habitacion = 'UCI-101'), '2025-03-01 10:00:00', '2025-03-08 14:30:00', 'Insuficiencia respiratoria'),
(2, (SELECT id_habitacion FROM cat_habitaciones WHERE numero_habitacion = 'UCI-103'), '2025-03-05 11:00:00', NULL, 'Infarto agudo de miocardio'),
(3, (SELECT id_habitacion FROM cat_habitaciones WHERE numero_habitacion = 'GEN-201'), '2025-03-10 09:30:00', '2025-03-12 18:00:00', 'Neumonía'),
(4, (SELECT id_habitacion FROM cat_habitaciones WHERE numero_habitacion = 'PED-301'), '2025-03-12 08:00:00', '2025-03-14 10:00:00', 'Deshidratación'),
(5, (SELECT id_habitacion FROM cat_habitaciones WHERE numero_habitacion = 'UCI-102'), '2025-03-15 22:00:00', '2025-03-18 11:00:00', 'Trauma craneoencefálico'),
(6, (SELECT id_habitacion FROM cat_habitaciones WHERE numero_habitacion = 'UCI-101'), '2025-03-20 13:00:00', NULL, 'Shock séptico');

-- Historiales clínicos
INSERT INTO historiales_clinicos (id_paciente, id_medico, fecha_registro, sintomas, diagnostico)
VALUES
(1, 1, '2025-03-01 10:15:00', 'Fiebre, tos, disnea', 'COVID-19 confirmado'),
(2, 2, '2025-03-05 11:20:00', 'Dolor torácico opresivo, sudoración', 'Infarto agudo de miocardio'),
(3, 3, '2025-03-10 09:45:00', 'Cefalea intensa, fotofobia', 'Migraña con aura'),
(4, 4, '2025-03-12 08:30:00', 'Tos productiva, fiebre', 'Neumonía adquirida en comunidad'),
(5, 5, '2025-03-15 22:30:00', 'Pérdida de conciencia, vómito', 'Trauma craneoencefálico leve'),
(6, 1, '2025-03-20 13:15:00', 'Hipotensión, fiebre alta, confusión', 'Shock séptico de origen abdominal');

-- 4. EVOLUCIÓN TRANSACCIONAL (Nivel 3)
-- ============================================================

-- Recetas médicas (relación 1:1 con historial)
INSERT INTO recetas_medicas (id_historial, fecha_emision)
SELECT id_historial, fecha_registro::date + 1
FROM historiales_clinicos;

-- Detalles de recetas (asociando medicamentos existentes)
-- Asignamos medicamentos según diagnóstico
INSERT INTO detalles_recetas (id_receta, id_medicamento, dosis, frecuencia, duracion_dias)
VALUES
-- Paciente 1 (COVID)
(1, (SELECT id_medicamento FROM cat_medicamentos WHERE nombre_comercial = 'Paracetamol'), '500 mg', 'Cada 8 horas', 5),
(1, (SELECT id_medicamento FROM cat_medicamentos WHERE nombre_comercial = 'Amoxicilina'), '500 mg', 'Cada 12 horas', 7),
-- Paciente 2 (Infarto)
(2, (SELECT id_medicamento FROM cat_medicamentos WHERE nombre_comercial = 'Losartán'), '50 mg', 'Cada 24 horas', 30),
-- Paciente 3 (Migraña)
(3, (SELECT id_medicamento FROM cat_medicamentos WHERE nombre_comercial = 'Ibuprofeno'), '400 mg', 'Cada 8 horas', 3),
-- Paciente 4 (Neumonía)
(4, (SELECT id_medicamento FROM cat_medicamentos WHERE nombre_comercial = 'Amoxicilina'), '1 g', 'Cada 12 horas', 10),
-- Paciente 5 (Trauma)
(5, (SELECT id_medicamento FROM cat_medicamentos WHERE nombre_comercial = 'Paracetamol'), '1 g', 'Cada 6 horas', 3),
-- Paciente 6 (Shock séptico)
(6, (SELECT id_medicamento FROM cat_medicamentos WHERE nombre_comercial = 'Omeprazol'), '40 mg', 'Cada 24 horas', 7),
(6, (SELECT id_medicamento FROM cat_medicamentos WHERE nombre_comercial = 'Ibuprofeno'), '400 mg', 'Cada 8 horas', 5);

-- ============================================================
-- FIN DEL DML DE PRUEBA
-- ============================================================