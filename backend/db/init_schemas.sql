-- Inicialización de esquemas para arquitectura Medallón
-- Bronze, Silver, Gold

CREATE SCHEMA IF NOT EXISTS bronze;
CREATE SCHEMA IF NOT EXISTS silver;
CREATE SCHEMA IF NOT EXISTS gold;

-- Comentarios descriptivos
COMMENT ON SCHEMA bronze IS 'Datos crudos de ingesta - textos extraídos, JSONs sin procesar';
COMMENT ON SCHEMA silver IS 'Datos limpios y normalizados - catálogos, normativas, resultados intermedios';
COMMENT ON SCHEMA gold IS 'Datos finales del negocio - matrices GTC 45 y RAM listas para exportar';

-- Grant permissions (ajustar según necesidades)
GRANT ALL ON SCHEMA bronze TO riesgo_admin;
GRANT ALL ON SCHEMA silver TO riesgo_admin;
GRANT ALL ON SCHEMA gold TO riesgo_admin;