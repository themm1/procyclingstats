"""
Script de prueba para verificar la funcionalidad de buscar resultados de carreras.
Este script prueba con carreras de años anteriores que deberían tener resultados disponibles.
"""

import sys
import os

# Add parent directory to path to import utilidades
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import utilidades as herramientas

def test_race_results():
    """Prueba obtener resultados de carreras conocidas"""
    
    # Prueba con carreras de 2024 y 2025 que deberían tener resultados
    test_races = [
        "race/tour-de-france/2024",
        "race/giro-d-italia/2024",
        "race/vuelta-a-espana/2024",
        "race/paris-roubaix/2024",
        "race/milano-sanremo/2024",
    ]
    
    print("=" * 80)
    print("🧪 PRUEBA DE RESULTADOS DE CARRERAS")
    print("=" * 80)
    
    for race_url in test_races:
        print(f"\n📍 Probando: {race_url}")
        print("-" * 80)
        
        try:
            df_results = herramientas.buscar_resultados_carrera(race_url)
            
            if df_results is not None and not df_results.empty:
                print(f"✅ ¡Éxito! Se encontraron {len(df_results)} resultados")
                print(f"\n📊 Primeros 3 resultados:")
                print(df_results.head(3).to_string())
                print("\n" + "=" * 80)
                return True  # Si encontramos al menos una carrera con resultados, es un éxito
            else:
                print(f"⚠️  No se encontraron resultados para esta carrera")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print("\n" + "=" * 80)
    print("⚠️  No se pudieron obtener resultados de ninguna carrera de prueba")
    print("💡 Esto puede deberse a:")
    print("   1. Problemas de conexión a ProCyclingStats")
    print("   2. Cambios en la estructura del sitio web")
    print("   3. Limitaciones de la API de procyclingstats")
    print("=" * 80)
    return False

if __name__ == "__main__":
    test_race_results()
