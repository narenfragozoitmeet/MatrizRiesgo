#====================================================================================================
# START - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================

# THIS SECTION CONTAINS CRITICAL TESTING INSTRUCTIONS FOR BOTH AGENTS
# BOTH MAIN_AGENT AND TESTING_AGENT MUST PRESERVE THIS ENTIRE BLOCK

# Communication Protocol:
# If the `testing_agent` is available, main agent should delegate all testing tasks to it.
#
# You have access to a file called `test_result.md`. This file contains the complete testing state
# and history, and is the primary means of communication between main and the testing agent.
#
# Main and testing agents must follow this exact format to maintain testing data. 
# The testing data must be entered in yaml format Below is the data structure:
# 
## user_problem_statement: {problem_statement}
## backend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.py"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## frontend:
##   - task: "Task name"
##     implemented: true
##     working: true  # or false or "NA"
##     file: "file_path.js"
##     stuck_count: 0
##     priority: "high"  # or "medium" or "low"
##     needs_retesting: false
##     status_history:
##         -working: true  # or false or "NA"
##         -agent: "main"  # or "testing" or "user"
##         -comment: "Detailed comment about status"
##
## metadata:
##   created_by: "main_agent"
##   version: "1.0"
##   test_sequence: 0
##   run_ui: false
##
## test_plan:
##   current_focus:
##     - "Task name 1"
##     - "Task name 2"
##   stuck_tasks:
##     - "Task name with persistent issues"
##   test_all: false
##   test_priority: "high_first"  # or "sequential" or "stuck_first"
##
## agent_communication:
##     -agent: "main"  # or "testing" or "user"
##     -message: "Communication message between agents"

# Protocol Guidelines for Main agent
#
# 1. Update Test Result File Before Testing:
#    - Main agent must always update the `test_result.md` file before calling the testing agent
#    - Add implementation details to the status_history
#    - Set `needs_retesting` to true for tasks that need testing
#    - Update the `test_plan` section to guide testing priorities
#    - Add a message to `agent_communication` explaining what you've done
#
# 2. Incorporate User Feedback:
#    - When a user provides feedback that something is or isn't working, add this information to the relevant task's status_history
#    - Update the working status based on user feedback
#    - If a user reports an issue with a task that was marked as working, increment the stuck_count
#    - Whenever user reports issue in the app, if we have testing agent and task_result.md file so find the appropriate task for that and append in status_history of that task to contain the user concern and problem as well 
#
# 3. Track Stuck Tasks:
#    - Monitor which tasks have high stuck_count values or where you are fixing same issue again and again, analyze that when you read task_result.md
#    - For persistent issues, use websearch tool to find solutions
#    - Pay special attention to tasks in the stuck_tasks list
#    - When you fix an issue with a stuck task, don't reset the stuck_count until the testing agent confirms it's working
#
# 4. Provide Context to Testing Agent:
#    - When calling the testing agent, provide clear instructions about:
#      - Which tasks need testing (reference the test_plan)
#      - Any authentication details or configuration needed
#      - Specific test scenarios to focus on
#      - Any known issues or edge cases to verify
#
# 5. Call the testing agent with specific instructions referring to test_result.md
#
# IMPORTANT: Main agent must ALWAYS update test_result.md BEFORE calling the testing agent, as it relies on this file to understand what to test next.

#====================================================================================================
# END - Testing Protocol - DO NOT EDIT OR REMOVE THIS SECTION
#====================================================================================================



#====================================================================================================
# Testing Data - Main Agent and testing sub agent both should log testing data below this section
#====================================================================================================

user_problem_statement: |
  WebApp completa para crear matriz de riesgos (identificación de peligros y valoración de riesgos en el marco del SG-SST).
  Debe soportar dos tipos de matrices:
  1. Matriz SST (GTC 45) - Seguridad y Salud en el Trabajo
  2. Matriz de Riesgos Legales
  
  Funcionalidades:
  - Upload de documentos (PDF, Word, Excel)
  - Procesamiento automático con IA (Google Gemini 2.5 Flash)
  - Generación de matrices estructuradas con metodologías RAM y GTC 45
  - Exportación a Excel con formato profesional
  - Historial de matrices generadas
  
  Stack:
  - Backend: Python 3.12, FastAPI, MongoDB, LangChain + LangGraph, emergentintegrations
  - Frontend: React 19, Tailwind CSS, shadcn/ui

backend:
  - task: "API Endpoint /api/v1/ingest - Upload y procesamiento de documentos"
    implemented: true
    working: "NA"
    file: "/app/backend/api/v1/unified_api.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado endpoint que recibe file, empresa y tipo_matriz. Procesa documento, extrae texto, ejecuta agentes y guarda en MongoDB"
      - working: "NA"
        agent: "testing"
        comment: "NO TESTEADO - Según instrucciones del review request, este endpoint no debe ser testeado todavía (requiere documento y tarda ~30-60 segundos con LLM)"

  - task: "Servicio de extracción de texto (PDF/Word/Excel)"
    implemented: true
    working: "NA"
    file: "/app/backend/services/document_extractor.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Implementado con PyMuPDF, python-docx y openpyxl. Extrae texto de los 3 formatos"
      - working: "NA"
        agent: "testing"
        comment: "NO TESTEADO - Servicio interno usado por /api/v1/ingest que no fue testeado según instrucciones"

  - task: "Integración con Google Gemini via emergentintegrations"
    implemented: true
    working: true
    file: "/app/backend/services/llm_service.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "LLM Service usando emergentintegrations con Gemini 2.5 Flash. EMERGENT_LLM_KEY configurado"
      - working: true
        agent: "testing"
        comment: "✅ VERIFICADO - Health check confirma LLM configurado correctamente: gemini/gemini-2.5-flash. EMERGENT_LLM_KEY presente en .env"

  - task: "Procesador Matriz SST (GTC 45)"
    implemented: true
    working: "NA"
    file: "/app/backend/services/matriz_sst_processor.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Agentes para identificar peligros SST y evaluar riesgos según GTC 45. Calcula nivel de deficiencia, exposición, probabilidad, consecuencia y nivel de riesgo"
      - working: "NA"
        agent: "testing"
        comment: "NO TESTEADO - Servicio interno usado por /api/v1/ingest que no fue testeado según instrucciones"

  - task: "Procesador Matriz Legal"
    implemented: true
    working: "NA"
    file: "/app/backend/services/matriz_legal_processor.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Agentes para identificar riesgos legales (contractual, cumplimiento, laboral, fiscal, etc.) y evaluar con metodología RAM"
      - working: "NA"
        agent: "testing"
        comment: "NO TESTEADO - Servicio interno usado por /api/v1/ingest que no fue testeado según instrucciones"

  - task: "Generador de Excel SST"
    implemented: true
    working: "NA"
    file: "/app/backend/services/excel_generator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Genera Excel profesional para matriz SST con colores por nivel de riesgo, todos los campos GTC 45"
      - working: "NA"
        agent: "testing"
        comment: "NO TESTEADO - Servicio interno usado por endpoints de export que requieren matrices existentes"

  - task: "Generador de Excel Legal"
    implemented: true
    working: "NA"
    file: "/app/backend/services/excel_generator.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Genera Excel para riesgos legales con categorías, normativa aplicable, impactos y acciones de mitigación"
      - working: "NA"
        agent: "testing"
        comment: "NO TESTEADO - Servicio interno usado por endpoints de export que requieren matrices existentes"

  - task: "API Endpoint /api/v1/matrix/{tipo}/{id} - Obtener matriz"
    implemented: true
    working: true
    file: "/app/backend/api/v1/unified_api.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Endpoint para obtener datos de matriz SST o Legal por ID desde MongoDB"
      - working: true
        agent: "testing"
        comment: "✅ TESTEADO - Endpoint responde correctamente con 404 para matrices inexistentes y 400 para tipos inválidos. Validación de parámetros funciona correctamente"

  - task: "API Endpoint /api/v1/matrix/{tipo}/{id}/export - Exportar Excel"
    implemented: true
    working: "NA"
    file: "/app/backend/api/v1/unified_api.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Endpoint para descargar matriz en formato Excel (.xlsx)"
      - working: "NA"
        agent: "testing"
        comment: "NO TESTEADO - Requiere matrices existentes para poder testear la funcionalidad de export"

  - task: "API Endpoint /api/v1/matrices - Listar todas las matrices"
    implemented: true
    working: true
    file: "/app/backend/api/v1/unified_api.py"
    stuck_count: 0
    priority: "medium"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Lista todas las matrices (SST y Legal) ordenadas por fecha"
      - working: true
        agent: "testing"
        comment: "✅ TESTEADO - Endpoint funciona correctamente. Retorna lista vacía [] como esperado (sin matrices creadas). Filtros por tipo (sst/legal) funcionan correctamente"

  - task: "MongoDB Connection y Collections"
    implemented: true
    working: true
    file: "/app/backend/db/mongodb.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Conexión MongoDB con 4 colecciones: documentos_bronze, analisis_silver, matrices_sst, matrices_legales"
      - working: true
        agent: "testing"
        comment: "✅ TESTEADO - MongoDB conectado correctamente en localhost:27017. Base de datos 'riesgo_ia' creada. Colecciones verificadas: documentos_bronze (0), matrices_sst (0), matrices_legales (0), analisis_silver (0). Health check confirma conexión activa"

  - task: "API Health Check y Documentación"
    implemented: true
    working: true
    file: "/app/backend/server.py"
    stuck_count: 0
    priority: "high"
    needs_retesting: false
    status_history:
      - working: true
        agent: "testing"
        comment: "✅ TESTEADO - GET /api/health retorna status:healthy, database:connected, llm:gemini/gemini-2.5-flash. GET /api/docs sirve Swagger UI correctamente. Backend root (localhost:8001) retorna info de la app correctamente"

frontend:
  - task: "HomePage - Selección tipo matriz y upload"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/HomePage.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "UI para seleccionar SST o Legal, upload documento, input empresa y generar matriz. Diseño neobrutalism"

  - task: "AnalysisPage - Visualización de matriz generada"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/AnalysisPage.js"
    stuck_count: 0
    priority: "high"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Muestra estadísticas de matriz (total, críticos, altos, medios, bajos), info metodología y botón descargar Excel"

  - task: "HistoryPage - Listado de matrices previas"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/pages/HistoryPage.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Lista todas las matrices con filtros (todas, SST, legal). Cards con stats y botón descarga directa"

  - task: "Router - Rutas actualizadas"
    implemented: true
    working: "NA"
    file: "/app/frontend/src/App.js"
    stuck_count: 0
    priority: "medium"
    needs_retesting: true
    status_history:
      - working: "NA"
        agent: "main"
        comment: "Ruta actualizada a /analysis/:tipo/:matrizId para soportar ambos tipos de matrices"

metadata:
  created_by: "main_agent"
  version: "2.1"
  test_sequence: 1
  run_ui: false

test_plan:
  current_focus:
    - "API Endpoint /api/v1/ingest - Upload y procesamiento de documentos"
    - "Servicio de extracción de texto (PDF/Word/Excel)"
    - "Procesador Matriz SST (GTC 45)"
    - "Procesador Matriz Legal"
    - "Generador de Excel SST"
    - "Generador de Excel Legal"
    - "API Endpoint /api/v1/matrix/{tipo}/{id}/export - Exportar Excel"
  stuck_tasks: []
  test_all: false
  test_priority: "high_first"

agent_communication:
  - agent: "main"
    message: |
      ✅ IMPLEMENTACIÓN COMPLETA FINALIZADA
      
      He implementado el sistema completo para generación de 2 tipos de matrices de riesgos:
      
      1. MATRIZ SST (GTC 45):
         - Identifica peligros: Físicos, Químicos, Biológicos, Ergonómicos, Psicosociales, etc.
         - Evalúa con metodología GTC 45: ND x NE x NC = NR
         - Genera Excel con formato profesional y colores
      
      2. MATRIZ RIESGOS LEGALES:
         - Identifica riesgos: Contractual, Cumplimiento, Laboral, Fiscal, Regulatorio, etc.
         - Evalúa con RAM: Probabilidad x [(ImpFinanciero + ImpReputacional + ImpOperacional)/3]
         - Genera Excel con normativa aplicable y acciones de mitigación
      
      ARQUITECTURA:
      - Backend: FastAPI + MongoDB + emergentintegrations (Gemini 2.5 Flash)
      - Agentes LLM: Extractor → Identificador → Evaluador
      - Frontend: React 19 + Tailwind CSS + Diseño Neobrutalism
      
      ENDPOINTS IMPLEMENTADOS:
      - POST /api/v1/ingest (file, empresa, tipo_matriz)
      - GET /api/v1/matrix/{tipo}/{id}
      - GET /api/v1/matrix/{tipo}/{id}/export
      - GET /api/v1/matrices
      
      SERVICIOS CORRIENDO:
      ✅ Backend (port 8001)
      ✅ Frontend (port 3000)
      ✅ MongoDB (port 27017)
      
      PENDIENTE: Testing completo del flujo end-to-end

  - agent: "testing"
    message: |
      🔍 TESTING BACKEND COMPLETADO - RESULTADOS EXITOSOS
      
      ✅ ENDPOINTS BÁSICOS TESTEADOS (según review request):
      - GET / (Frontend HTML) ✅
      - GET /api/health ✅ (Status: healthy, DB: connected, LLM: gemini/gemini-2.5-flash)
      - GET /api/docs ✅ (Swagger UI accesible)
      - GET /api/v1/matrices ✅ (Lista vacía [], correcto)
      - GET /api/v1/matrices?tipo=sst ✅ (Filtros funcionan)
      - GET /api/v1/matrices?tipo=legal ✅
      
      ✅ VALIDACIONES TESTEADAS:
      - GET /api/v1/matrix/sst/nonexistent-id → 404 ✅
      - GET /api/v1/matrix/invalid/some-id → 400 ✅
      
      ✅ INFRAESTRUCTURA VERIFICADA:
      - MongoDB: Conectado en localhost:27017 ✅
      - Base de datos: riesgo_ia ✅
      - Colecciones: documentos_bronze, matrices_sst, matrices_legales ✅
      - Supervisor: Todos los servicios corriendo ✅
      
      ❌ NO TESTEADO (según instrucciones):
      - POST /api/v1/ingest (requiere documento, tarda 30-60s con LLM)
      - Servicios internos (document_extractor, processors, excel_generator)
      - Endpoints de export (requieren matrices existentes)
      
      📊 RESULTADO: 8/8 tests básicos PASARON (100% success rate)
      🎯 Backend está listo para testing end-to-end con documentos reales