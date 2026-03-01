#!/usr/bin/env python3
"""
Identificador de Tool Calls en Conversaciones Sintéticas
=========================================================
Analiza trefa_conversations_chatml.jsonl y conversacion_chatml_pares.jsonl
para identificar patrones de herramientas, escenarios únicos y conversaciones
candidatas para etiquetado con IA.

Uso:
    python3 identificar_tools_sinteticos.py [directorio_archivos]
    
    Si no se pasa argumento, busca en el directorio actual.
    
Salida:
    - identificacion_tools_report.json   → Reporte completo
    - candidatas_etiquetado.jsonl         → Conversaciones con tools para IA
    - candidatas_sin_tools_unicas.jsonl   → Conversaciones sin tools pero únicas
"""

import json
import re
import sys
import os
import hashlib
from collections import defaultdict, Counter
from pathlib import Path

# ── Configuración ──────────────────────────────────────────────
ARCHIVOS_BUSCAR = [
]

# Herramientas conocidas de Mariana
TOOLS_CONOCIDAS = {
    "buscar_vehiculos", "obtener_vehiculo", "buscar_alternativas",
    "comparar_vehiculos", "estadisticas_inventario", "calcular_financiamiento",
    "buscar_informacion", "obtener_info_negocio", "obtener_faqs",
    "solicitar_datos_contacto", "enviar_cotizacion_email",
}

# Patrones para detectar tool calls en diferentes formatos
TOOL_CALL_PATTERNS = [
    # Formato Qwen ChatML: <tool_call>\n{"name": "...", "arguments": {...}}\n</tool_call>
    re.compile(r'<tool_call>\s*\{[^}]*"name"\s*:\s*"(\w+)"', re.DOTALL),
    # Formato function_call
    re.compile(r'"function_call"\s*:\s*\{[^}]*"name"\s*:\s*"(\w+)"'),
    # Formato Action/Action Input
    re.compile(r'Action:\s*(\w+)\s*\nAction Input:'),
    # Formato tool_calls array
    re.compile(r'"tool_calls"\s*:\s*\[\s*\{[^}]*"name"\s*:\s*"(\w+)"'),
    # Formato directo función()
    re.compile(r'\b(buscar_vehiculos|obtener_vehiculo|buscar_alternativas|comparar_vehiculos|estadisticas_inventario|calcular_financiamiento|buscar_informacion|obtener_info_negocio|obtener_faqs|solicitar_datos_contacto|enviar_cotizacion_email)\s*\('),
]

# Patrones de escenarios por contenido del usuario
ESCENARIO_PATTERNS = {
    "ESC-1_no_inventario": [r'no\s+tienen', r'no\s+hay', r'no\s+encuentr'],
    "ESC-2_precio_general": [r'cuánto\s+cuestan', r'qué\s+precios', r'rango\s+de\s+precios'],
    "ESC-3_financiamiento": [r'financ', r'crédit', r'mensualidad', r'enganche', r'plazos?'],
    "ESC-4_documentos": [r'document', r'papel', r'requisito', r'qué\s+necesito'],
    "ESC-5_garantia": [r'garant[íi]a', r'cubre', r'falla', r'descompon'],
    "ESC-6_ubicacion": [r'ubicaci[óo]n', r'sucursal', r'direcci[óo]n', r'horario', r'd[óo]nde\s+están'],
    "ESC-7_tradein": [r'intercambio', r'cambiar\s+mi\s+auto', r'tomar\s+a\s+cuenta', r'trade'],
    "ESC-8_devolucion": [r'devoluci[óo]n', r'devolver', r'regresar\s+el\s+auto'],
    "ESC-9_comparar": [r'compar', r'cu[áa]l\s+es\s+mejor', r'diferencia\s+entre'],
    "ESC-10_fuera_tema": [r'seguro\s+de\s+auto', r'refacci[óo]n', r'taller', r'rent', r'mecánic'],
    "ESC-11_frustrado": [r'quej', r'molest', r'frustr', r'enojad', r'pésim', r'terrible'],
    "ESC-12_saludo": [r'^hola\s*$', r'^buenas?\s*(tardes|noches|días|d[íi]as)?\.?\s*$', r'^hey\s*$', r'^qué\s+tal'],
    "ESC-13_ambiguo": [r'^quiero\s+uno', r'^cuánto\s+cuesta\??$', r'^me\s+interesa$', r'^información$'],
    "ESC-14_stats": [r'cuántos\s+autos', r'inventario', r'qué\s+marcas'],
    "ESC-15_visita": [r'prueba\s+de\s+manejo', r'verlo\s+en\s+persona', r'visitar'],
    "ESC-16_proceso": [r'c[óo]mo\s+compro', r'proceso\s+de\s+compra', r'c[óo]mo\s+funciona'],
    "ESC-17_cotizacion": [r'cotizaci[óo]n', r'correo', r'email', r'mand[ae]'],
    "LIM-1_legal": [r'impuesto', r'fiscal', r'deduci', r'legal', r'seguro\s+de'],
    "LIM-3_negociar": [r'descuento', r'rebaj', r'negoci', r'menos', r'más\s+barato', r'igualar'],
    "LIM-5_reservar": [r'reserv', r'apart', r'guard', r'depósito'],
    "LIM-6_bot": [r'robot', r'bot', r'real\s+o', r'humano', r'persona\s+real', r'inteligencia\s+artificial'],
    "LIM-7_mecanico": [r'diagnóstic', r'ruido', r'falla\s+mecánic', r'confiable', r'problem'],
}


def detectar_tools(mensaje: str) -> list[str]:
    """Detecta tool calls en un mensaje de assistant."""
    tools = []
    for pattern in TOOL_CALL_PATTERNS:
        matches = pattern.findall(mensaje)
        for m in matches:
            if m in TOOLS_CONOCIDAS:
                tools.append(m)
    return tools


def detectar_escenario(mensaje_usuario: str) -> list[str]:
    """Clasifica un mensaje de usuario en escenarios."""
    msg_lower = mensaje_usuario.lower().strip()
    escenarios = []
    for esc, patterns in ESCENARIO_PATTERNS.items():
        for p in patterns:
            if re.search(p, msg_lower):
                escenarios.append(esc)
                break
    return escenarios


def hash_conversacion(messages: list) -> str:
    """Hash único basado en primer mensaje de usuario."""
    for m in messages:
        if m.get("role") == "user":
            return hashlib.md5(m.get("content", "")[:200].encode()).hexdigest()
    return hashlib.md5(str(messages).encode()).hexdigest()


def analizar_archivo(filepath: str) -> dict:
    """Analiza un archivo JSONL completo."""
    resultados = {
        "archivo": filepath,
        "total": 0,
        "con_tools": 0,
        "sin_tools": 0,
        "tools_por_conversacion": Counter(),
        "combos_tools": Counter(),
        "escenarios_detectados": Counter(),
        "escenario_x_tool": defaultdict(Counter),
        "conversaciones_con_tools": [],
        "conversaciones_unicas_sin_tools": [],
        "formatos_tool_call": Counter(),
        "errores": 0,
    }
    
    hashes_vistos = set()
    
    with open(filepath, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, 1):
            try:
                data = json.loads(line.strip())
            except json.JSONDecodeError:
                resultados["errores"] += 1
                continue
            
            messages = data.get("messages", data.get("conversations", []))
            if not messages:
                continue
            
            resultados["total"] += 1
            
            # Dedup
            h = hash_conversacion(messages)
            if h in hashes_vistos:
                continue
            hashes_vistos.add(h)
            
            # Detectar tools
            tools_en_conv = []
            tiene_tool_response = False
            primer_user_msg = ""
            
            for msg in messages:
                role = msg.get("role", "")
                content = msg.get("content", "")
                
                if role == "user" and not primer_user_msg:
                    primer_user_msg = content
                
                if role == "assistant":
                    found = detectar_tools(content)
                    tools_en_conv.extend(found)
                    
                    # Detectar formato de tool call
                    if "<tool_call>" in content:
                        resultados["formatos_tool_call"]["qwen_chatml"] += 1
                    elif "function_call" in content:
                        resultados["formatos_tool_call"]["function_call"] += 1
                    elif "Action:" in content:
                        resultados["formatos_tool_call"]["action_input"] += 1
                
                if role == "tool":
                    tiene_tool_response = True
            
            # Clasificar
            if tools_en_conv:
                resultados["con_tools"] += 1
                for t in tools_en_conv:
                    resultados["tools_por_conversacion"][t] += 1
                
                combo = tuple(sorted(set(tools_en_conv)))
                resultados["combos_tools"][combo] += 1
                
                # Guardar para etiquetado
                resultados["conversaciones_con_tools"].append({
                    "linea": line_num,
                    "hash": h,
                    "tools": tools_en_conv,
                    "combo": list(combo),
                    "tiene_tool_response": tiene_tool_response,
                    "primer_msg_usuario": primer_user_msg[:200],
                    "n_mensajes": len(messages),
                    "data": data,  # conversación completa
                })
            else:
                resultados["sin_tools"] += 1
            
            # Detectar escenarios
            escenarios = detectar_escenario(primer_user_msg)
            for esc in escenarios:
                resultados["escenarios_detectados"][esc] += 1
                for t in tools_en_conv:
                    resultados["escenario_x_tool"][esc][t] += 1
            
            # Conversaciones sin tools pero con escenario interesante
            if not tools_en_conv and escenarios:
                n_turnos = len([m for m in messages if m.get("role") == "user"])
                if n_turnos >= 2:
                    resultados["conversaciones_unicas_sin_tools"].append({
                        "linea": line_num,
                        "hash": h,
                        "escenarios": escenarios,
                        "primer_msg_usuario": primer_user_msg[:200],
                        "n_mensajes": len(messages),
                        "n_turnos": n_turnos,
                    })
    
    return resultados


def generar_reporte(resultados_por_archivo: list, output_dir: str):
    """Genera reporte consolidado y archivos de salida."""
    
    # Consolidar
    total_convs = sum(r["total"] for r in resultados_por_archivo)
    total_con_tools = sum(r["con_tools"] for r in resultados_por_archivo)
    tools_global = Counter()
    combos_global = Counter()
    escenarios_global = Counter()
    esc_x_tool_global = defaultdict(Counter)
    formatos_global = Counter()
    
    todas_con_tools = []
    todas_unicas_sin = []
    
    for r in resultados_por_archivo:
        tools_global += r["tools_por_conversacion"]
        combos_global += r["combos_tools"]
        escenarios_global += r["escenarios_detectados"]
        formatos_global += r["formatos_tool_call"]
        for esc, tc in r["escenario_x_tool"].items():
            esc_x_tool_global[esc] += tc
        todas_con_tools.extend(r["conversaciones_con_tools"])
        todas_unicas_sin.extend(r["conversaciones_unicas_sin_tools"])
    
    # Identificar combos ÚNICOS (que aparecen pocas veces)
    combos_raros = {k: v for k, v in combos_global.items() if v <= 3}
    combos_frecuentes = {k: v for k, v in combos_global.items() if v > 3}
    
    # Reporte JSON
    reporte = {
        "resumen": {
            "total_conversaciones": total_convs,
            "con_tool_calling": total_con_tools,
            "sin_tool_calling": total_convs - total_con_tools,
            "porcentaje_tools": round(total_con_tools / max(total_convs, 1) * 100, 1),
            "formatos_detectados": dict(formatos_global),
        },
        "herramientas": {
            "uso_por_herramienta": dict(tools_global.most_common()),
            "herramientas_no_encontradas": list(TOOLS_CONOCIDAS - set(tools_global.keys())),
        },
        "combinaciones_tools": {
            "frecuentes": {" + ".join(k): v for k, v in sorted(combos_frecuentes.items(), key=lambda x: -x[1])[:20]},
            "raras_unicas": {" + ".join(k): v for k, v in sorted(combos_raros.items(), key=lambda x: -x[1])[:30]},
            "total_combos_distintos": len(combos_global),
        },
        "escenarios": {
            "detectados": dict(escenarios_global.most_common()),
            "escenario_x_herramienta": {
                esc: dict(tc.most_common(5)) 
                for esc, tc in sorted(esc_x_tool_global.items())
            },
        },
        "candidatas_etiquetado": {
            "con_tools": len(todas_con_tools),
            "sin_tools_unicas": len(todas_unicas_sin),
        },
        "archivos_analizados": [
            {"archivo": r["archivo"], "total": r["total"], "con_tools": r["con_tools"], "errores": r["errores"]}
            for r in resultados_por_archivo
        ],
    }
    
    # Guardar reporte
    reporte_path = os.path.join(output_dir, "identificacion_tools_report.json")
    with open(reporte_path, "w", encoding="utf-8") as f:
        json.dump(reporte, f, indent=2, ensure_ascii=False)
    print(f"📊 Reporte: {reporte_path}")
    
    # Guardar candidatas con tools (para etiquetado con IA)
    candidatas_path = os.path.join(output_dir, "candidatas_etiquetado.jsonl")
    with open(candidatas_path, "w", encoding="utf-8") as f:
        for c in todas_con_tools:
            entry = {
                "messages": c["data"].get("messages", c["data"].get("conversations", [])),
                "metadata": {
                    "tools_detectadas": c["tools"],
                    "combo": c["combo"],
                    "tiene_tool_response": c["tiene_tool_response"],
                    "primer_msg_usuario": c["primer_msg_usuario"],
                    "hash": c["hash"],
                    "origen": "sintetico_identificado",
                }
            }
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    print(f"🔧 Candidatas con tools: {candidatas_path} ({len(todas_con_tools)} conversaciones)")
    
    # Guardar únicas sin tools
    unicas_path = os.path.join(output_dir, "candidatas_sin_tools_unicas.jsonl")
    with open(unicas_path, "w", encoding="utf-8") as f:
        for c in todas_unicas_sin:
            f.write(json.dumps(c, ensure_ascii=False) + "\n")
    print(f"📝 Sin tools únicas: {unicas_path} ({len(todas_unicas_sin)} conversaciones)")
    
    # Imprimir resumen
    print(f"\n{'═' * 60}")
    print(f"RESUMEN DE IDENTIFICACIÓN")
    print(f"{'═' * 60}")
    print(f"Total conversaciones: {total_convs}")
    print(f"Con tool calling: {total_con_tools} ({reporte['resumen']['porcentaje_tools']}%)")
    print(f"Formatos: {dict(formatos_global)}")
    print(f"\nHerramientas encontradas ({len(tools_global)}):")
    for t, n in tools_global.most_common():
        print(f"  {t}: {n}")
    
    no_encontradas = reporte["herramientas"]["herramientas_no_encontradas"]
    if no_encontradas:
        print(f"\n⚠️  Herramientas NO encontradas: {', '.join(no_encontradas)}")
    
    print(f"\nCombinaciones únicas: {len(combos_global)}")
    print(f"  Frecuentes (>3): {len(combos_frecuentes)}")
    print(f"  Raras (≤3): {len(combos_raros)}")
    
    print(f"\nEscenarios detectados:")
    for esc, n in escenarios_global.most_common():
        print(f"  {esc}: {n}")


def main():
    directorio = sys.argv[1] if len(sys.argv) > 1 else "."
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "."
    
    print(f"Buscando archivos en: {directorio}")
    
    archivos_encontrados = []
    for nombre in ARCHIVOS_BUSCAR:
        path = os.path.join(directorio, nombre)
        if os.path.exists(path):
            archivos_encontrados.append(path)
            print(f"  ✅ {nombre}")
        else:
            print(f"  ❌ {nombre} — no encontrado")
    
    # También buscar cualquier .jsonl en el directorio
    for f in Path(directorio).glob("*.jsonl"):
        if str(f) not in archivos_encontrados and f.name not in [a.split("/")[-1] for a in archivos_encontrados]:
            print(f"  📄 Archivo adicional encontrado: {f.name}")
    
    if not archivos_encontrados:
        print("\n⚠️  No se encontraron archivos. Pasa el directorio como argumento:")
        print(f"   python3 {sys.argv[0]} /ruta/a/training-files/gold-conversations")
        sys.exit(1)
    
    resultados = []
    for path in archivos_encontrados:
        print(f"\nAnalizando {os.path.basename(path)}...")
        r = analizar_archivo(path)
        resultados.append(r)
    
    generar_reporte(resultados, output_dir)


if __name__ == "__main__":
    main()

